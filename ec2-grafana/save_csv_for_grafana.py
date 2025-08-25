import boto3
import pandas as pd
import time
from decimal import Decimal
import os
from datetime import datetime
# AWS 설정
dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-2")

# Decimal 타입 → int/float 자동 변환용
def normalize(item):
    def convert(val):
        if isinstance(val, Decimal):
            if val % 1 == 0:
                return int(val)
            else:
                return float(val)
        return val
    return {k: convert(v) for k, v in item.items()}

# 공통 함수: 테이블 → CSV 저장
def save_table_to_csv(table_name, file_name, rename_map=None, column_order=None):
    table = dynamodb.Table(table_name)
    response = table.scan()
    items = [normalize(i) for i in response['Items']]
    df = pd.DataFrame(items)

    # 컬럼명 바꾸기 (조인 편하게 하기 위해)
    if rename_map:
        df.rename(columns=rename_map, inplace=True)

    # 컬럼 순서 지정
    if column_order:
        df = df[column_order]

    df.to_csv(file_name, index=False)
    print(f"✅ {file_name} 저장 완료")
def append_flag_table_to_csv(table_name, file_name, rename_map=None, column_order=None):
    table = dynamodb.Table(table_name)
    response = table.scan()
    items = [normalize(i) for i in response['Items']]
    df = pd.DataFrame(items)

    # ✅ timestamp 추가
    df['timestamp'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    # ✅ 컬럼명 변환
    if rename_map:
        df.rename(columns=rename_map, inplace=True)

    # ✅ 컬럼 순서
    if column_order:
        column_order = column_order + ['timestamp']
        df = df[column_order]

    # ✅ append 저장
    df.to_csv(file_name, index=False, mode='a', header=not os.path.exists(file_name))
    print(f"📈 {file_name} append 완료 ({len(df)}건)")
# 5분마다 갱신
while True:
    try:
        # 1. zone-count-dynamodb → zone.csv
        save_table_to_csv("zone-count-dynamodb", "./data/zone-count-dynamodb.csv")

        # 2. pickup-zone-dynamodb → pickup.csv
        save_table_to_csv(
            "pickup-zone-dynamodb",
            "./data/pickup-zone-dynamodb.csv",
            column_order=["pickup_zone_id", "count"]
        )

        # 3. flag-dynamodb → flag.csv (key-value 테이블)
        append_flag_table_to_csv("flag-dynamodb", "./data/flag-dynamodb.csv")

        # 4. taxi-destination-dynamodb → destination.csv
        save_table_to_csv("taxi-destination-dynamodb", "./data/taxi-destination-dynamodb.csv")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    time.sleep(30)