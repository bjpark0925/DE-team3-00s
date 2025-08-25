CREATE TABLE IF NOT EXISTS daily_zone_stats (
    date DATE PRIMARY KEY,
    max_pickup_zone_id VARCHAR(20),
    max_pickup_count INTEGER,
    min_pickup_zone_id VARCHAR(20),
    min_pickup_count INTEGER,
    dispatch_count INTEGER,
    pickup_count INTEGER,
    dispatch_success_rate FLOAT
);
