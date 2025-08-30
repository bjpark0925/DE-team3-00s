import psycopg2
import json
import os
from datetime import datetime

# 현재 날짜 기준
today = datetime.now().date()

# DB 연결 정보 불러오기
config_path = os.path.join("config", "db_config.json")
with open(config_path, "r") as f:
    config = json.load(f)

DB_HOST = config["host"]
DB_PORT = config["port"]
DB_NAME = "daily_stats_db"
DB_USER = config["user"]
DB_PASSWORD = config["password"]

print(f"📌 {today} 날짜 기준 dispatch_pickup_diff 업데이트 중...")

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()

    # 해당 날짜의 모든 행 업데이트
    cursor.execute("""
        UPDATE zone_hourly_activity_log
        SET dispatch_pickup_diff = dispatch_count - pickup_count
        WHERE date = %s
    """, (today,))

    conn.commit()
    print("✅ dispatch_pickup_diff 업데이트 완료")

except Exception as e:
    print("❌ 오류 발생:", e)

finally:
    if conn:
        cursor.close()
        conn.close()
