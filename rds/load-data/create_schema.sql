-- 스키마 생성 (존재하지 않으면 새로 생성)
CREATE SCHEMA IF NOT EXISTS nyc_tlc_data;

-- 1. 예상 픽업 테이블
-- 한 달 단위로 write, 초 단위로 read
CREATE TABLE IF NOT EXISTS nyc_tlc_data.expected_pickups (
    pickup_zone_id SMALLINT,
    pickup_hour SMALLINT,
    expected_pickup FLOAT
);

-- 2. 인접 존 테이블
-- 한 달 단위로 write, 초 단위로 read
CREATE TABLE IF NOT EXISTS nyc_tlc_data.adjacent_zones (
    zone_id SMALLINT,
    adjacent_zone_id SMALLINT[]
);
