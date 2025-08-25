import boto3
import psycopg2
import json
from decimal import Decimal
from datetime import datetime
import os

# Load configs
with open('config/aws_config.json') as f:
    aws_config = json.load(f)

with open('config/db_config.json') as f:
    db_config = json.load(f)

# AWS clients
dynamodb = boto3.resource('dynamodb', region_name=aws_config['region_name'])
pickup_table = dynamodb.Table(aws_config['pickup_table'])  # pickup-zone-dynamodb-s
flag_table = dynamodb.Table(aws_config['flag_table'])      # flag-dynamodb-s

print("📥 DynamoDB → pickup 테이블 스캔 중...")
pickup_response = pickup_table.scan()
items = pickup_response['Items']

# 예외 처리
if not items:
    print("🚫 DynamoDB에서 가져온 pickup 데이터가 없습니다.")
    exit()

# zone_id: str, count: Decimal('N')
max_zone = max(items, key=lambda x: int(x['count']))
min_zone = min(items, key=lambda x: int(x['count']))

max_zone_id = max_zone['zone_id']
max_pickup_count = int(max_zone['count'])

min_zone_id = min_zone['zone_id']
min_pickup_count = int(min_zone['count'])

print("📥 DynamoDB → flag 테이블 조회 중...")
dispatch_item = flag_table.get_item(Key={'counter_type': 'dispatch'})['Item']
pickup_item = flag_table.get_item(Key={'counter_type': 'pickup'})['Item']

dispatch_count = int(dispatch_item['count'])
pickup_count = int(pickup_item['count'])

success_rate = round(pickup_count / dispatch_count, 3) if dispatch_count else 0.0

# 오늘 날짜
today = datetime.now().strftime('%Y-%m-%d')

# RDS 연결
print("📝 RDS → daily_zone_stats 테이블에 저장 중...")
conn = psycopg2.connect(
    host=db_config['host'],
    port=db_config['port'],
    user=db_config['user'],
    password=db_config['password'],
    database=db_config['database']
)
cursor = conn.cursor()

cursor.execute("""
    INSERT INTO daily_zone_stats (
        date, max_pickup_zone_id, max_pickup_count,
        min_pickup_zone_id, min_pickup_count,
        dispatch_count, pickup_count, dispatch_success_rate
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (date) DO NOTHING
""", (
    today, max_zone_id, max_pickup_count,
    min_zone_id, min_pickup_count,
    dispatch_count, pickup_count, success_rate
))

conn.commit()
cursor.close()
conn.close()

print("✅ RDS 저장 완료!")

# 🔁 DynamoDB 초기화
print("🧹 DynamoDB 초기화 중...")

# 1. pickup 테이블 초기화
with pickup_table.batch_writer() as batch:
    for item in items:
        batch.delete_item(Key={'zone_id': item['zone_id']})

# 2. flag 테이블 초기화
flag_table.delete_item(Key={'counter_type': 'dispatch'})
flag_table.delete_item(Key={'counter_type': 'pickup'})

print("🧼 초기화 완료! 모든 작업이 정상적으로 끝났습니다.")
