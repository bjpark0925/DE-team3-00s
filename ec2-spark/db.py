import psycopg2
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# 환경변수에서 값 불러오기
conn = psycopg2.connect(
    host=os.getenv("PG_HOST"),
    port=os.getenv("PG_PORT"),
    dbname=os.getenv("PG_DB"),
    user=os.getenv("PG_USER"),
    password=os.getenv("PG_PASSWORD"),
    sslmode=os.getenv("PG_SSLMODE")
)


cur = conn.cursor()

sql = """
DROP TABLE IF EXISTS adjacent_zones;

CREATE TABLE adjacent_zones AS
SELECT
    pickup_zone_id AS zone_id,
    ARRAY_AGG(DISTINCT dropoff_zone_id) AS adjacent_zone_ids
FROM
    pick_dropoff_zones
GROUP BY
    pickup_zone_id;

DROP TABLE IF EXISTS pick_dropoff_zones;
"""

cur.execute(sql)
conn.commit()
cur.close()
conn.close()
