import time
import random
import requests
import threading
import pandas as pd

from datetime import datetime
from datetime import timedelta


API_URL = "your-api-url"


ride_logs_df = pd.read_csv("manhattan_rides_2024_03_01_18_to_19.csv")
ride_logs_df["matched"] = False
ride_logs_df.rename(columns={"tpep_pickup_datetime": "timestamp"}, inplace=True)
ride_logs_df["timestamp"] = pd.to_datetime(ride_logs_df["timestamp"]).apply(lambda x: x.isoformat())
ride_logs = ride_logs_df.to_dict("records")


# 10배속
acceleration = 10


class Taxi:
    def __init__(self, taxi_id, start_zone, end_time):
        self.taxi_id = taxi_id
        self.current_zone = start_zone
        self.end_time = end_time

    def move(self):
        payload = {
            "taxi_id": self.taxi_id,
            "location_id": self.current_zone,
        }
        requests.post(API_URL + "/simulation/request_place", json=payload)

        # 시뮬레이션 시작 기준 시각
        now = datetime(2024, 3, 1, 18, 0, 0)

        while now < self.end_time:
            matched_ride = None

            # 미래 5분 이내 ride 중 매칭되는 것 찾기
            for ride in ride_logs:
                ride_time = datetime.fromisoformat(ride["timestamp"])
                if ride["matched"]:
                    continue
                if self.current_zone == ride["PULocationID"] and now <= ride_time <= now + timedelta(minutes=5):
                    matched_ride = ride
                    break

            if matched_ride:
                # 승차 처리
                matched_ride["matched"] = True
                payload = {"taxi_id": self.taxi_id}
                try:
                    requests.post(API_URL + "/request_ride", json=payload)
                    print(f"[승차] 🚕 taxi {self.taxi_id} matched ride → {matched_ride['PULocationID']} @ {ride_time.time()}")
                    self.current_zone = matched_ride["DOLocationID"]
                except Exception as e:
                    print(f"[{self.taxi_id}] ride error: {e}")
                time_spent = random.uniform(540 / acceleration, 600 / acceleration)
                time.sleep(time_spent)  # 9~10분
                now += timedelta(seconds=time_spent * acceleration)
                payload = {"taxi_id": self.taxi_id, "location_id": self.current_zone}
                response = requests.post(API_URL + "/simulation/request_place", json=payload)
                print(f"[하차 후 배차] 🚕 taxi {self.taxi_id} : {self.current_zone} → {response.json()}")
            else:
                # 승차 매칭 안 되면 배차
                payload = {"taxi_id": self.taxi_id, "location_id": self.current_zone}
                try:
                    response = requests.post("http://15.164.180.106:8000/simulation/request_place", json=payload)
                    next_zone = response.json()
                    self.current_zone = next_zone
                    print(f"[배차] taxi {self.taxi_id}: {payload['location_id']} → {next_zone}")
                except Exception as e:
                    print(f"[{self.taxi_id}] Error: {e}")
                time_spent = random.uniform(240 / acceleration, 300 / acceleration)
                time.sleep(time_spent)  # 4~5분
                now += timedelta(seconds=time_spent * acceleration)


def simulate_taxis(n_taxis=100):
    threads = []
    end_time = datetime(2024, 3, 1, 19, 0, 0)  # 1시간 동안만 시뮬레이션
    for i in range(n_taxis):
        start_zone = 164
        taxi = Taxi(taxi_id=i+1, start_zone=start_zone, end_time=end_time)
        thread = threading.Thread(target=taxi.move)
        threads.append(thread)
        thread.start()

    for t in threads:
        t.join()


if __name__ == "__main__":
    simulate_taxis(n_taxis=1000)
    # 시뮬레이션 결과를 csv 파일로 저장
    matched_rides = [ride for ride in ride_logs if ride["matched"]]
    matched_df = pd.DataFrame(matched_rides)
    matched_df.to_csv("matched_rides.csv", index=False)
    print(f"Matched rides saved to matched_rides.csv")
