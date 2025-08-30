import sys
import json
import boto3
import psycopg2
from datetime import datetime
from decimal import Decimal

# 🟩 실행 모드 설정
mode = sys.argv[1] if len(sys.argv) > 1 else "both"

# 📦 Config 파일 로드
with open("config/aws_config.json") as f:
    aws_config = json.load(f)

with open("config/db_config.json") as f:
    db_config = json.load(f)

# 🟡 DynamoDB 리소스 연결 (IAM Role 기반 인증)
session = boto3.Session(region_name=aws_config["region_name"])
dynamo = session.resource("dynamodb")

# 🗂️ 테이블 이름
DISPATCH_TABLE_NAME = aws_config["dispatch_table"]
PICKUP_TABLE_NAME = aws_config["pickup_table"]

dispatch_table = dynamo.Table(DISPATCH_TABLE_NAME)
pickup_table = dynamo.Table(PICKUP_TABLE_NAME)

# 🕒 현재 날짜, 시간 구하기
now = datetime.now()
current_date = now.date()
current_hour = now.hour  # 0~23 (int)

# 🐘 PostgreSQL 연결
db_conn = psycopg2.connect(
    host=db_config["host"],
    database=db_config["database"],
    user=db_config["user"],
    password=db_config["password"],
    port=db_config.get("port", 5432)
)
cursor = db_conn.cursor()

# 🚕 1. Dispatch: 5분마다 누적
if mode in ["both", "dispatch_only"]:
    dispatch_items = dispatch_table.scan().get("Items", [])
    for item in dispatch_items:
        zone_id = item["zone_id"]
        count = int(item["count"]) if isinstance(item["count"], Decimal) else item["count"]

        cursor.execute("""
            INSERT INTO zone_hourly_activity_log (date, hour, zone_id, dispatch_count)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (date, hour, zone_id)
            DO UPDATE SET dispatch_count = zone_hourly_activity_log.dispatch_count + EXCLUDED.dispatch_count;
        """, (current_date, current_hour, zone_id, count))

# 🚕 2. Pickup: 1시간마다 누적
if mode in ["both", "pickup_only"]:
    pickup_items = pickup_table.scan().get("Items", [])
    for item in pickup_items:
        zone_id = item["zone_id"]
        count = int(item["count"]) if isinstance(item["count"], Decimal) else item["count"]

        cursor.execute("""
            INSERT INTO zone_hourly_activity_log (date, hour, zone_id, pickup_count)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (date, hour, zone_id)
            DO UPDATE SET pickup_count = zone_hourly_activity_log.pickup_count + EXCLUDED.pickup_count;
        """, (current_date, current_hour, zone_id, count))

# 💾 커밋 및 종료
db_conn.commit()
cursor.close()
db_conn.close()

print(f"✅ {current_date} {current_hour}시 ({mode}) 데이터 저장 완료")
