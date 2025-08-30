# 📦 DynamoDB → RDS Daily Stats ETL

택시 승차 데이터를 하루 단위로 집계하여, DynamoDB의 데이터를 PostgreSQL RDS에 저장하고, 매일 03시에 자동으로 데이터를 초기화하는 **ETL 파이프라인**입니다.

---

## 📊 테이블에 저장할 데이터

1. **일간 zone별 승차 횟수 관련 통계**  
   - `pickup-zone-dynamodb-s`에서 하루 동안 누적된 데이터를 가져와 RDS에 저장합니다.

2. **일간 총 배차, 승차 횟수 관련 통계**  
   - `flag-dynamodb-s`에서 하루 동안 누적된 데이터를 가져와 RDS에 저장합니다.  
   - 저장된 데이터를 활용해 **일간 배차 성공률**도 계산합니다.  
   - 이 값은 미리 계산하여 저장되며, **Grafana 등의 시각화 도구가 연산 없이 바로 읽을 수 있도록** 설계되었습니다.

3. **시간대별 zone 통계 및 diff 저장** 🔄  
   - `pickup-zone-dynamodb-s`와 `flag-dynamodb-s` 데이터를 5분 또는 1시간 단위로 수집하여, 시간대별로 정리한 zone 통계를 `zone_diff_stats` 테이블에 저장합니다.
   - 주요 컬럼: `timestamp`, `zone_id`, `dispatch_count`, `pickup_count`, `dispatch_minus_pickup`

   **✅ 왜 이런 작업을 했는가?**  
   기존 시스템에서는 한 달마다만 zone 추천 모델이 업데이트되어, 현실을 제대로 반영하지 못하는 한계가 있었습니다. 이를 보완하기 위해, **전날의 실적 데이터를 다음날 바로 반영**하려는 의도로 이 작업을 수행했습니다.  
   특히, `dispatch - pickup` 값이 **작을수록 추천 점수를 높이고**, **클수록 낮추는 방식**으로 개선을 시도하려고 합니다. 이는 매일매일 추천 점수에 유연한 변화를 줄 수 있게 해주며, 추후엔 실험을 통해 적절한 가중치를 찾을 계획입니다.

---

## 🛠️ DB 정의

모든 테이블은 RDS의 `daily_stats_db`라는 별도 DB에 저장됩니다.  
RDS에서는 논리적으로 여러 DB를 둘 수 있는데, 다음과 같이 **기능별로 분리**하여 관리합니다:

### 1. `postgres` DB
- **Spark** 작업 결과물 저장용
- 예시 테이블:
  ```
  postgres=> \dt
               List of relations
   Schema |       Name       | Type  | Owner 
  --------+------------------+-------+-------
   public | adjacent_zones   | table | de3
   public | expected_pickups | table | de3
  (2 rows)
  ```

### 2. `daily_stats_db` DB
- **일일 통계 (배차/승차 등)** 저장용
- 예시 테이블:
  ```
  daily_stats_db=> \dt
               List of relations
   Schema |       Name       | Type  | Owner 
  --------+------------------+-------+-------
   public | daily_zone_stats | table | de3
  --------+------------------+-------+-------
   public | zone_hourly_activity_log | table | de3
  (2 row)
  ```

> 💡 이러한 DB 분리는 추후 **접근 권한 분리**에도 유용합니다.  
예를 들어:
- `postgres` DB는 EC2의 Spark, API 서버만 접근하도록 제한  
- `daily_stats_db` DB는 DynamoDB 수집기와 Grafana(시각화 도구)만 접근 가능하게 설정

---

## 📁 프로젝트 구조

```
dynamo-to-rds/
├── config/
│   ├── aws_config.json          
│   └── db_config.json           
├── schema/
│   └── create_table.sql         
├── scripts/
│   ├── sync_daily_stats.py      
│   ├── sync_and_reset_daily_stats.py  
│   └── sync_zone_diff_stats.py
├── requirements.txt             
└── README.md
```

---

## 📊 데이터 구조

### DynamoDB 테이블

1. `pickup-zone-dynamodb-s`
   ```json
   {
     "zone_id": "Midtown Center",
     "count": 276
   }
   ```

2. `flag-dynamodb-s`
   ```json
   {
     "counter_type": "dispatch", "count": 8145
   },
   {
     "counter_type": "pickup", "count": 2061
   }
   ```

---

## 🔧 설정 파일

### config/aws_config.json

```json
{
  "region_name": "ap-northeast-2",
  "pickup_table": "pickup-zone-dynamodb-s",
  "flag_table": "flag-dynamodb-s"
}
```

### config/db_config.json

```json
{
  "host": "<RDS_HOST>",
  "port": 5432,
  "database": "daily_stats_db",
  "user": "de3",
  "password": "<YOUR_PASSWORD>"
}
```

---

## ⚙️ 실행 방법

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. RDS 테이블 생성

```bash
psql -h <RDS_HOST> -U de3 -d daily_stats_db -f schema/create_table.sql
```

### 3. 수동 실행 (테스트용)

```bash
python3 scripts/sync_and_reset_daily_stats.py
python3 scripts/sync_zone_diff_stats.py  # ← 시간대별 diff 저장
```

---

## 🕒 자동 실행: Crontab 등록

```bash
crontab -e
```

```cron
# 일간 통계 (03시)
0 3 * * * /usr/bin/python3 /home/ubuntu/dynamo-to-rds/scripts/sync_and_reset_daily_stats.py >> /home/ubuntu/dynamo-to-rds/logs/daily_sync.log 2>&1

# 시간대별 통계 (5분 단위 실행 예시)
*/5 * * * * /usr/bin/python3 /home/ubuntu/dynamo-to-rds/scripts/sync_zone_diff_stats.py >> /home/ubuntu/dynamo-to-rds/logs/diff_sync.log 2>&1
```

> 로그 저장용 `/home/ubuntu/dynamo-to-rds/logs/` 디렉토리도 미리 생성하세요.

---

## ✏️ 예시 결과

```sql
SELECT * FROM daily_zone_stats ORDER BY date DESC LIMIT 1;
2025-08-25 | Midtown Center | 276 | Seaport | 1 | 8145 | 2061 | 0.253

SELECT * FROM zone_diff_stats ORDER BY timestamp DESC LIMIT 5;
2025-08-25 09:00:00 | Midtown Center | 53 | 12 | 41
2025-08-25 08:00:00 | Upper East Side | 44 | 42 | 2
...
```