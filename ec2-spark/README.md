# ec2-spark

## 📌 개요

EC2 인스턴스에서 Docker 기반 Spark 클러스터를 자동으로 구성하고,

NYC Taxi 데이터를 분석하여 결과를 PostgreSQL에 저장하는 전체 파이프라인을 구현

`app.py`는 Spark 작업 수행, `db.py`는 PostgreSQL 테이블 최적화를 담당

---

## 실행 환경

- **Docker / ubuntu:22.04**
- **Apache Spark 3.5.6, PySpark 3.5.6**
- **PostgreSQL**

---

## 📁 디렉토리 구조

```
ec2-spark
├── app.py                  # 메인 Spark 분석 스크립트
├── db.py                   # PostgreSQL 테이블 후처리 스크립트
└── README.md               # ec2-spark 설명
```

---

## 🔁 전체 아키텍처 흐름

1. EC2 인스턴스가 시작되면 `user-data.sh`를 통해 다음 작업이 자동 수행됨:
   - 필수 패키지 및 Docker 설치
   - ECR에서 Spark 이미지 pull
   - `docker-compose.yml` 자동 생성 및 Spark 클러스터 실행

2. Docker Compose를 통해 다음 컨테이너들이 생성됩니다:
   - `spark-master`: Spark 마스터 노드
   - `spark-worker1`, `spark-worker2`: 워커 노드 2개

3. Spark 마스터가 정상 작동하면, 다음 단계의 ETL 파이프라인이 실행됩니다:
   - `spark-submit`으로 `app.py` 제출
   - **Extract**: S3에서 NYC 택시 데이터 로드
   - **Transform**:
     - 유효성 검사 및 전처리 (시간 조건, 금액 필터 등)
     - 예상 픽업량(`expected_pickups`), 인접 지역(`pick_dropoff_zones`) 계산
   - **Load**:
     - 두 개의 결과 테이블을 PostgreSQL로 저장

4. Spark 작업 종료 후 `db.py`를 실행하여 다음 작업 수행:
   - 중복된 데이터를 정리하고 최종 `adjacent_zones` 테이블 생성
   - 불필요한 중간 테이블 제거
   - PySpark의 collect_list, collect_set 결과를 그대로 JDBC로 넘겨 저장할 경우 데이터 타입 매핑 에러 발생 가능성이 존재하여
   - 행 단위로 저장한 다음 db.py를 PostgreSQL 내부에서 ARRAY_AGG() 수행

이 흐름은 완전 **자동화**되어 있으며, EC2 인스턴스 생성과 동시에 Spark 기반 ETL 파이프라인이 실행되고 PostgreSQL에 데이터가 적재됨

---

## 🚀 실행 방법

1. **API서버에서 EC2 Launch Template을 통한 ec2 생성**

2. **user-data.sh 주요 작업**
    - `docker`, `awscli`, `docker-compose` 설치
    - ECR에서 이미지 pull
    - `docker-compose.yml` 자동 생성 및 실행
    - `spark-submit app.py` 실행
    - 이후 `db.py`를 실행하여 PostgreSQL 후처리

3. **Docker Compose 구성 (3노드)**
    - `spark-master`
    - `spark-worker1` CPU cores: 2, Memory : 2G
    - `spark-worker2` CPU cores: 2, Memory : 2G

4. **Spark 제출 예시**
    ```bash
    docker exec -it spark-master spark-submit       --master spark://master:7077       --deploy-mode client       ...
      app.py
    ```

---

## 📊 app.py 주요 기능

- **데이터 로딩**: S3 (NYC Taxi Data)
- **필터링/전처리**: 총액, 시간 조건, zone ID 유효성 필터
- **`expected_pickups` 생성**:
  - (pickup_zone_id, pickup_hour) 기준 시간당 평균 픽업 수
- **`pick_dropoff_zones` 생성**:
  - 평균 이동시간 5분 미만인 dropoff_zone_id만 추출
- **PostgreSQL 저장**

---

## 🧩 db.py 주요 기능

- `pick_dropoff_zones`를 기준으로 `adjacent_zones` 생성
  - `ARRAY_AGG(DISTINCT dropoff_zone_id)` 사용
- 불필요 테이블 정리 (`DROP TABLE IF EXISTS`)
- 최종적으로 `adjacent_zones`만 남음

---

## ⚙️ 환경 설정 파일

- `spark-env.sh`:
    - 마스터 주소, 포트, 워커 설정, 로그 디렉토리 정의
    - `PYSPARK_PYTHON=python3` 지정

- `dockerfile`: Spark 및 Python 실행 환경 포함

- `user-data.sh`: 전체 EC2 초기 부팅 자동화
    - Docker 설치 → ECR 로그인 → docker-compose 생성 및 실행 → spark-submit → db.py 실행

---


## 📎 주의 사항

- `.env` 파일은 컨테이너에 반드시 공유되어야 함
- ECR 로그인 시 region, 계정 번호 정확히 입력할 것
- PostgreSQL에는 해당 스키마 권한 필요
