CREATE TABLE IF NOT EXISTS zone_hourly_activity_log (
    date DATE NOT NULL,
    hour SMALLINT NOT NULL,  -- 0~23 시간 단위
    zone_id VARCHAR(100) NOT NULL,
    dispatch_count INTEGER DEFAULT 0,
    pickup_count INTEGER DEFAULT 0,
    dispatch_pickup_diff INTEGER DEFAULT 0,  -- dispatch - pickup 차이 저장

    PRIMARY KEY (date, hour, zone_id)
);
