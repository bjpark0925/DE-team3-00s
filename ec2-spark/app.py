import os
from dotenv import load_dotenv
from pyspark.sql import SparkSession, functions as F
from pyspark.storagelevel import StorageLevel
from pyspark.sql.functions import explode

# -----------------------------
# 환경변수 로드 (.env에서)
# -----------------------------
load_dotenv()

PG_URL = f"jdbc:postgresql://{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DB')}?sslmode={os.getenv('PG_SSLMODE')}"
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")

# -----------------------------
# SparkSession (최적화 옵션)
# -----------------------------
spark = (
    SparkSession.builder
    .appName("NYC_Taxi_DATA_PROCESSING")
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    .config("spark.hadoop.fs.s3a.endpoint", "s3.ap-northeast-2.amazonaws.com")
    .config("spark.hadoop.fs.s3a.path.style.access", "true")
    .config("spark.sql.adaptive.enabled", "true")
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
    .config("spark.sql.shuffle.partitions", "200")
    .config("spark.sql.parquet.filterPushdown", "true")
    .config("spark.sql.parquet.enableVectorizedReader", "true")
    .getOrCreate()
)

# Manhattan LocationID (69개)
MANHATTAN_IDS = [
    4, 12, 13, 24, 41, 43, 45, 48, 50,
    68, 74, 75, 79, 87, 88, 90, 100,
    107, 113, 114, 125, 137,
    140, 141, 142, 143, 144, 148, 151, 158,
    161, 162, 163, 164, 166, 170, 186, 209,
    211, 224, 229, 230, 231, 232, 233, 234, 236, 237,
    238, 239, 246, 249, 261, 262, 263
]

# -----------------------------
# 1) S3 로드
# -----------------------------
df = spark.read.parquet("s3a://nyc-tlc-softeer/nyc_taxi/")

# -----------------------------
# 2) 공통 전처리
# -----------------------------
base = (
    df.select(
        F.col("PULocationID").cast("smallint").alias("pickup_zone_id"),
        F.col("DOLocationID").cast("smallint").alias("dropoff_zone_id"),
        F.col("tpep_pickup_datetime").cast("timestamp").alias("pickup_ts"),
        F.col("tpep_dropoff_datetime").cast("timestamp").alias("dropoff_ts"),
        F.col("total_amount").cast("float").alias("total_amount")
    )
    .filter(
        F.col("pickup_zone_id").isNotNull() &
        F.col("dropoff_zone_id").isNotNull() &
        F.col("pickup_ts").isNotNull() &
        F.col("dropoff_ts").isNotNull() &
        F.col("total_amount").isNotNull() &
        (F.col("total_amount") > 0) &
        (F.col("pickup_ts") < F.col("dropoff_ts")) &  # ← 이 줄 추가
        ((F.col("dropoff_ts").cast("long") - F.col("pickup_ts").cast("long")) / 60.0 <= 720)
    )
)
base_with_hour = base.withColumn("pickup_hour", F.hour("pickup_ts").cast("smallint"))
base_with_hour = base_with_hour.persist(StorageLevel.MEMORY_AND_DISK)

# -----------------------------
# 테이블 A: expected_pickup
# -----------------------------
# expected_pickup 테이블 생성
# pickup_zone_id와 pickup_hour를 기준으로 그룹화하여 해당 시간대의 픽업 건수를 계산
# 이때, 각 픽업 지역에 대해 18개월 동안의 픽업 건수를 540으로 나누어 시간당 예상 픽업 건수로 변환
# 이 과정에서 각 지역과 시간대별로 예상 픽업 건수를 계산하고
# 최종적으로 pickup_zone_id와 pickup_hour를 기준으로 그룹화하여 예상 픽업 건수를 계산
table_A = (
    base_with_hour
    .select("pickup_zone_id", "pickup_hour")
    .filter(F.col("pickup_zone_id").isin(MANHATTAN_IDS))
    .repartition("pickup_zone_id", "pickup_hour")
    .groupBy("pickup_zone_id", "pickup_hour")
    .agg(F.count(F.lit(1)).cast("int").alias("expected_pickup"))
    .withColumn("expected_pickup", (F.col("expected_pickup") / 540).cast("int"))
)



base_with_hour_duration = base_with_hour.withColumn(
    "duration_min",
    ((F.col("dropoff_ts").cast("long") - F.col("pickup_ts").cast("long")) / 60.0)
)


base_with_avg_duration = (
    base_with_hour_duration
    .filter(
        F.col("pickup_zone_id").isin(MANHATTAN_IDS) &
        F.col("dropoff_zone_id").isin(MANHATTAN_IDS)
    )
    .repartition("pickup_zone_id", "dropoff_zone_id", "pickup_hour")
    .groupBy("pickup_zone_id", "dropoff_zone_id", "pickup_hour")
    .agg(F.round(F.avg("duration_min"), 2).cast("float").alias("avg_duration"))  # FLOAT
)



# -----------------------------
# 테이블 B: pick_dropoff_zones
# -----------------------------
# avg_duration가 5분 미만인 경우에 대해서만 인접 지역을 찾고, dropoff_zone_id를 리스트로 모은 후 explode하여 행 단위로 풀어냄
# 이 과정에서 dropoff_zone_id는 리스트로 먼저 모으고, explode를 통해 행 단위로 풀어냄
# 최종적으로 dropoff_zone_id를 행 단위로 풀어내고, 불필요한 원본 리스트는 제거함    
table_B = (
    base_with_avg_duration
    .filter(F.col("avg_duration") < 5)
    .groupBy("pickup_zone_id")
    .agg(F.collect_set("dropoff_zone_id").alias("adjacent_zone_id"))  # 리스트로 먼저 모으고
    .withColumn("dropoff_zone_id", explode(F.col("adjacent_zone_id")))  # 리스트를 행 단위로 풀고
    .drop("adjacent_zone_id")  # 불필요한 원본 리스트 제거
)


# -----------------------------
# PostgreSQL에 저장
# -----------------------------

# expected_pickup 테이블과 pick_dropoff_zones 테이블을 PostgreSQL에 저장
table_A.write \
    .format("jdbc") \
    .option("url", PG_URL) \
    .option("dbtable", "expected_pickups") \
    .option("user", PG_USER) \
    .option("password", PG_PASSWORD) \
    .option("driver", "org.postgresql.Driver") \
    .mode("overwrite") \
    .save()

# pick_dropoff_zones 테이블을 PostgreSQL에 저장
table_B.write \
    .format("jdbc") \
    .option("url", PG_URL) \
    .option("dbtable", "pick_dropoff_zones") \
    .option("user", PG_USER) \
    .option("password", PG_PASSWORD) \
    .option("driver", "org.postgresql.Driver") \
    .mode("overwrite") \
    .save()


spark.stop()