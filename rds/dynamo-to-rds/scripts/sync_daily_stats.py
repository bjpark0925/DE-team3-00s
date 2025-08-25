import boto3
import psycopg2
import json
from decimal import Decimal
from datetime import datetime

# 📥 설정 파일 로드
with open('config/aws_config.json') as f:
    aws_config = json.load(f)

with open('config/db_config.json') as f:
    db_config = json.load(f)

# 📦 DynamoDB 리소스 초기화
dynamodb = boto3.resource('dynamodb', region_name=aws_config['region_name'])

pickup_table = dynamodb.Table(aws_config['pickup_table'])  # pickup-zone-dynamodb-s
flag_table = dynamodb.Table(aws_config['flag_table'])      # flag-dynamodb-s

# 📅 오늘 날짜
today = datetime.now().strftime('%Y-%m-%d')

print("📥 DynamoDB → pickup-zone-dynamodb-s 스캔 중...")
response = pickup_table.scan()
items = response['Items']

# 예외 방지: count는 Decimal이므로 int로 변환
max_zone = max(items, key=lambda x: int(x['count']))
min_zone = min(items, key=lambda x: int(x['count']))

print("📥 DynamoDB → flag-dynamodb-s 조회 중...")
dispatch_item = flag_table.get_item(Key={'counter_type': 'dispatch'})
pickup_item = flag_table.get_item(Key={'counter_type': 'pickup'})

dispatch_count = int(dispatch_item['Item']['count'])
pickup_count = int(pickup_item['Item']['count'])

dispatch_success_rate = round(pickup_count / dispatch_count, 4) if dispatch_count else 0.0

# 🧩 RDS 연결
conn = psycopg2.connect(
    host=db_config['host'],
    port=db_config['port'],
    user=db_config['user'],
    password=db_config['password'],
    database=db_config['database']
)
cursor = conn.cursor()

# 📤 daily_zone_stats에 저장
cursor.execute("""
    INSERT INTO daily_zone_stats (
        date, max_pickup_zone_id, max_pickup_count,
        min_pickup_zone_id, min_pickup_count,
        dispatch_count, pickup_count, dispatch_success_rate
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (date) DO UPDATE SET
        max_pickup_zone_id = EXCLUDED.max_pickup_zone_id,
        max_pickup_count = EXCLUDED.max_pickup_count,
        min_pickup_zone_id = EXCLUDED.min_pickup_zone_id,
        min_pickup_count = EXCLUDED.min_pickup_count,
        dispatch_count = EXCLUDED.dispatch_count,
        pickup_count = EXCLUDED.pickup_count,
        dispatch_success_rate = EXCLUDED.dispatch_success_rate
""", (
    today,
    max_zone['zone_id'], int(max_zone['count']),
    min_zone['zone_id'], int(min_zone['count']),
    dispatch_count, pickup_count, dispatch_success_rate
))

conn.commit()
cursor.close()
conn.close()

print("✅ RDS 저장 완료:", today)
