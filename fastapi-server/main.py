import asyncio

import geopandas as gpd

from fastapi import FastAPI
from pydantic import BaseModel
from shapely.geometry import Point


# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI()


# 택시존 SHP 파일 읽기
zones = gpd.read_file('taxi_zones/taxi_zones.shp')
zones = zones.to_crs(epsg=4326)


# 요청 본문 유효성 검사를 위한 Pydantic 모델 정의
class Item(BaseModel):
    name: str
    price: float
    is_offer: bool | None = None


# 택시 좌표 모델
class Coord(BaseModel):
    taxi_id: int
    lat: float
    lon: float


# 메인 페이지
@app.get("/")
def main_page():
    return "Hello Softeer!"


# 택시 좌표 변환 함수
def convert_lonlat_to_zone(point):
    matched_zone = zones[zones.contains(point)]
    return matched_zone.iloc[0]


# 택시 장소 요청 비동기 처리
@app.post("/request")
async def request_place(coord: Coord):
    point = Point(coord.lon, coord.lat)
    zone = await asyncio.to_thread(convert_lonlat_to_zone, point)

    if zone.empty:
        return "Coordinate doesn't match to any NYC TLC zones"

    return zone['zone']
