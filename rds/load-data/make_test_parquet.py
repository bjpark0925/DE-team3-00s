import os
import pandas as pd

base = os.path.expanduser("~/nyc_test_parquet")
os.makedirs(base, exist_ok=True)

# 1) expected_pickups (pickup_zone_id SMALLINT, pickup_hour SMALLINT, expected_pickup FLOAT)
df_expected = pd.DataFrame({
    "pickup_zone_id": pd.Series([1, 2, 2], dtype="int16"),
    "pickup_hour":    pd.Series([9, 18, 23], dtype="int16"),
    "expected_pickup": pd.Series([123.0, 250.5, 80.0], dtype="float64"),
})
df_expected.to_parquet(os.path.join(base, "expected_pickups.parquet"), index=False)

# 2) adjacent_zones (zone_id SMALLINT, adjacent_zone_id SMALLINT[])
#    파이썬 리스트를 그대로 배열로 저장합니다.
df_adj = pd.DataFrame({
    "zone_id": pd.Series([10, 20], dtype="int16"),
    "adjacent_zone_id": [
        [11, 12, 13],
        [21, 22]
    ],
})
df_adj.to_parquet(os.path.join(base, "adjacent_zones.parquet"), index=False)

print("Parquet files written to:", base)
