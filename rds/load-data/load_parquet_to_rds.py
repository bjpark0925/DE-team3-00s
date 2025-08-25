import os
import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus

# --- 환경변수 ---
DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "postgres")
DB_USER = os.environ["DB_USER"]
DB_PASS = os.environ["DB_PASS"]

DB_URL = f"postgresql+psycopg2://{DB_USER}:{quote_plus(DB_PASS)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DB_URL, connect_args={"sslmode": "require"})

base = os.path.expanduser("~/nyc_test_parquet")
SCHEMA = "nyc_tlc_data"

# 1) expected_pickups 적재 (append)
df_expected = pd.read_parquet(os.path.join(base, "expected_pickups.parquet"))
# 타입 맞추기 (선택): 이미 맞춘 상태지만 한 번 더 보정
df_expected = df_expected.astype({
    "pickup_zone_id": "int16",
    "pickup_hour": "int16",
    "expected_pickup": "float64",
})
df_expected.to_sql("expected_pickups", engine, schema=SCHEMA, if_exists="append", index=False)

# 2) adjacent_zones 적재 (append)
df_adj = pd.read_parquet(os.path.join(base, "adjacent_zones.parquet"))
# psycopg2가 파이썬 list를 PostgreSQL 배열로 자동 매핑합니다.
# 리스트 안 원소가 numpy 정수일 수 있으니 int로 변환해 안전하게 만듭니다.
df_adj["adjacent_zone_id"] = df_adj["adjacent_zone_id"].apply(lambda xs: [int(x) for x in xs])

df_adj = df_adj.astype({"zone_id": "int16"})
df_adj.to_sql("adjacent_zones", engine, schema=SCHEMA, if_exists="append", index=False)

print("Loaded into RDS successfully.")
