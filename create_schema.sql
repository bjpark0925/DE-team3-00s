-- 스키마 생성 (존재하지 않으면 새로 생성)
CREATE SCHEMA IF NOT EXISTS nyc_tlc_data;

-- 1. 예상 픽업 테이블
-- 한 달 단위로 write, 초 단위로 read
CREATE TABLE IF NOT EXISTS nyc_tlc_data.expected_pickups (
    pickup_zone_id SMALLINT,
    pickup_hour SMALLINT,
    expected_pickup INTEGER
);

-- 2. 존 이동 소요 시간 테이블
-- 한번 write 후 거의 수정 없음, 초 단위 read
CREATE TABLE IF NOT EXISTS nyc_tlc_data.zone_travel_duration (
    pickup_zone_id SMALLINT,
    dropoff_zone_id SMALLINT,
    pickup_hour SMALLINT,
    duration FLOAT
);

-- 3. 존 평균 요금 테이블
-- 한 달 단위로 write, 초 단위로 read
CREATE TABLE IF NOT EXISTS nyc_tlc_data.zone_avg_amount (
    pickup_zone_id SMALLINT,
    pickup_hour SMALLINT,
    avg_total_amount FLOAT
);
