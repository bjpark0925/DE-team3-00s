import os
import boto3
import asyncio
import psycopg2

import geopandas as gpd

from fastapi import FastAPI
from datetime import datetime
from pydantic import BaseModel
from shapely.geometry import Point
from collections import defaultdict
from contextlib import asynccontextmanager


# 택시존 SHP 파일 읽기
zones = gpd.read_file('taxi_zones/taxi_zones.shp')
zones = zones.to_crs(epsg=4326)


# 택시 좌표 모델
class Coord(BaseModel):
    taxi_id: int
    lat: float
    lon: float


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- 서버 시작 시 실행될 코드 ---
    print("Initializing FastAPI server...")

    # RDS에 연결 후 zone별 시간별 탑승 DB와 인접 Zone DB 로딩
    app.state.ride_count = defaultdict(int)
    app.state.adj_zones = defaultdict(list)

    # --- DynamoDB 연결을 위한 클라이언트 생성
    app.state.dynamo_client = boto3.client('dynamodb', region_name='ap-northeast-2')

    # --- RDS 연결을 위한 클라이언트 생성
    rds_client = boto3.client('rds', region_name='ap-northeast-2')
    db_instance_identifier = 'rds-taxi-db'

    response = rds_client.describe_db_instances(
        DBInstanceIdentifier=db_instance_identifier
    )

    db_instance = response['DBInstances'][0]

    # DB 접속에 필요한 정보들을 RDS API를 통해 가져옴
    db_endpoint = db_instance['Endpoint']['Address']
    db_port = db_instance['Endpoint']['Port']
    db_username = db_instance['MasterUsername']

    print(f"DB Endpoint: {db_endpoint}")
    print(f"DB Port: {db_port}")
    print(f"DB Username: {db_username}")

    # RDS 인스턴스 내에 postgres에 연결
    db_password = os.environ['RDS_PW']

    conn = psycopg2.connect(
        host=db_endpoint,
        port=db_port,
        user=db_username,
        password=db_password,
        dbname='postgres'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expected_pickups")
    for row in cursor:
        zone_id, hour, average_pickup = row
        app.state.ride_count[(zone_id, hour)] = average_pickup
    cursor.execute("SELECT * FROM adjacent_zones")
    for row in cursor:
        zone_id, adjacent_zone = row
        app.state.adj_zones[zone_id] = adjacent_zone
    print("Connected to RDS database")

    # --- RDS 연결을 위한 클라이언트 생성 끝 ---

    print("Ready for starting server")
    yield  # yield를 기준으로 이전은 시작, 이후는 종료 코드가 됩니다.
    # --- 서버 종료 시 실행될 코드 ---


# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI(lifespan=lifespan)


# 메인 페이지
@app.get("/")
def main_page():
    return "Hello Softeer!"


# 택시 좌표 변환 함수
def convert_lonlat_to_zone(point):
    matched_zone = zones[zones.contains(point)]
    if matched_zone.empty:
        return None
    return matched_zone.iloc[0]['LocationID']


# 택시 장소 요청 비동기 처리
@app.post("/request_place")
async def request_place(coord: Coord):
    # 1. GIS 좌표를 이용하여 현재 택시의 zone_id를 확인
    point = Point(coord.lon, coord.lat)
    current_zone_id = await asyncio.to_thread(convert_lonlat_to_zone, point)

    if current_zone_id is None:
        return "Coordinate doesn't match to any NYC TLC zones"

    # 2. Dynamo DB로부터 현재 택시가 연속 배차 요청인지 확인함
    next_zone_id = app.state.dynamo_client.get_item(
        TableName='taxi-destination-dynamodb',
        Key={'taxi_id': {'N': str(coord.taxi_id)}}
    ).get('Item', {})
    if next_zone_id:
        next_zone_id = next_zone_id.get('next_zone_id', {}).get('N')

    # 3. 다음 zone 계산
    adjacent_zones = app.state.adj_zones[current_zone_id]
    next_zone_counts_response = app.state.dynamo_client.batch_get_item(
        RequestItems={
            'zone-count-dynamodb': {
                'Keys': [{'zone_id': {'N': str(zone_id)}} for zone_id in adjacent_zones]
            }
        }
    )
    next_zone_counts = {
        int(item['zone_id']['N']): int(item.get('count', {}).get('N', '0'))
        for item in next_zone_counts_response.get('Responses', {}).get('zone-count-dynamodb', [])
    }

    max_score, max_zone_id = 0, 0

    if next_zone_id and next_zone_id in adjacent_zones:
        # 연속 배차 요청인 경우, 이전 목적지 zone의 count를 임시로 1 감소시켜 점수 계산
        original_count = next_zone_counts.get(next_zone_id, 0)
        next_zone_counts[next_zone_id] = max(0, original_count - 1)

    for zone_id in adjacent_zones:
        # DB에서 가져온 count가 있으면 사용하고, 없으면 0으로 간주
        count = next_zone_counts.get(zone_id, 0)

        temp_count = count
        # 만약 연속 배차 요청이고, 해당 zone이 이전 목적지였다면 임시로 count 1 감소
        if next_zone_id and zone_id == next_zone_id:
            temp_count = max(0, count - 1)

        # 모든 zone은 택시 1대가 추가되는 상황을 가정하고 점수 계산
        hour = datetime.now().hour
        score = app.state.ride_count.get((zone_id, hour), 0) / (temp_count + 1)
        if score > max_score:
            max_score, max_zone_id = score, zone_id

    if next_zone_id and next_zone_id != max_zone_id:
        # 떠나는 zone의 count를 1 감소. count 속성이 존재할 때만 실행
        app.state.dynamo_client.update_item(
            TableName='zone-count-dynamodb',
            Key={'zone_id': {'N': str(next_zone_id)}},
            UpdateExpression='SET #rc = #rc - :dec',
            ConditionExpression='attribute_exists(#rc) AND #rc > :zero',
            ExpressionAttributeNames={'#rc': 'count'},
            ExpressionAttributeValues={':dec': {'N': '1'}, ':zero': {'N': '0'}}
        )

    elif next_zone_id == max_zone_id:
        # 연속 배차 요청이지만 이전 목적지와 동일한 경우
        return max_zone_id

    # 다음 목적지로 가는 택시의 count를 1 증가
    app.state.dynamo_client.update_item(
        TableName='zone-count-dynamodb',
        Key={'zone_id': {'N': str(max_zone_id)}},
        UpdateExpression='SET #rc = if_not_exists(#rc, :start) + :inc',
        ExpressionAttributeNames={'#rc': 'count'},
        ExpressionAttributeValues={':inc': {'N': '1'}, ':start': {'N': '0'}}
    )

    # 택시의 다음 목적지 zone_id 업데이트
    app.state.dynamo_client.update_item(
        TableName='taxi-destination-dynamodb',
        Key={'taxi_id': {'N': str(coord.taxi_id)}},
        UpdateExpression='SET next_zone_id = :next_zone_id',
        ExpressionAttributeValues={':next_zone_id': {'N': str(max_zone_id)}}
    )

    # dynamo db에 log 작성
    app.state.dynamo_client.put_item(
        TableName='log-dynamodb',
        Item={
            'taxi_id': {'N': str(coord.taxi_id)},
            'timestamp': {'S': str(datetime.now())},
            'flag': {'N': '0'},
            'zone_id': {'N': str(current_zone_id)}
        }
    )

    return max_zone_id


@app.post("/request_ride")
async def request_ride(taxi_id: int):
    # 1. Dynamo DB로부터 요청한 택시의 next_zone_id 확인
    zone_id = app.state.dynamo_client.get_item(
        TableName='zone-count-dynamodb',
        Key={'taxi_id': {'N': str(taxi_id)}}
    ).get('Item', {}).get('zone_id', {}).get('N')

    if not zone_id:
        return "Taxi ID doesn't exist"

    # 2. 그 zone_id의 count를 -1 이후 업데이트
    count = app.state.dynamo_client.get_item(
        TableName='zone-count-dynamodb',
        Key={'zone_id': {'N': str(zone_id)}}
    ).get('Item', {}).get('count', {}).get('N')

    count = int(count) - 1

    app.state.dynamo_client.update_item(
        TableName='zone-count-dynamodb',
        Key={'zone_id': {'N': str(zone_id)}},
        UpdateExpression='SET count = :val',
        ExpressionAttributeValues={':val': {'N': str(count)}}
    )

    # dynamo db에 log 작성
    app.state.dynamo_client.put_item(
        TableName='log-dynamodb',
        Item={
            'taxi_id': {'N': str(taxi_id)},
            'timestamp': {'S': str(datetime.now())},
            'flag': {'N': '1'},
            'zone_id': {'N': str(zone_id)}
        }
    )

    # 3. 요청 성공 메시지 반환
    return "success"
