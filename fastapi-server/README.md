# 실시간 운행 지역 추천 API 서버

## 1. 시스템 아키텍처

본 시스템은 다음과 같은 구성 요소와 기술 스택을 활용합니다.

-   **API Server (FastAPI)**: `main.py`
    -   Python 기반의 고성능 비동기 웹 프레임워크인 FastAPI를 사용하여 핵심 API를 구축합니다.
    -   택시의 위치를 수신하고, 추천 장소를 계산하여 반환하는 로직을 수행합니다.
-   **Data Storage (AWS)**:
    -   **AWS RDS (PostgreSQL)**: 정적인 데이터를 저장합니다.
        -   `expected_pickups`: 시간대별, 지역(Zone)별 평균 승차 횟수 (과거 데이터 기반)
        -   `adjacent_zones`: 각 Zone에 인접한 Zone들의 목록
    -   **AWS DynamoDB**: 실시간으로 변하는 동적 데이터를 관리하는 NoSQL 데이터베이스입니다.
        -   `zone-count-dynamodb`: 현재 각 Zone으로 이동 중인 택시의 대수를 실시간으로 추적합니다.
        -   `taxi-destination-dynamodb`: 각 택시에게 추천된 목적지 Zone 정보를 저장합니다.
        -   `log-dynamodb`: 시스템의 모든 요청 및 응답을 기록하여 모니터링 및 추후 분석에 활용합니다.
-   **Data Processing (AWS Lambda)**:
    -   `invoke_taxi_parquet_lambda.sh` 스크립트를 통해 유추할 수 있듯이, 주기적으로 NYC TLC의 원본 데이터(Parquet 파일)를 처리하여 RDS의 통계 데이터를 업데이트하는 AWS Lambda 함수가 백그라운드에서 동작합니다.
    -   cron을 사용하여 매일 한 번씩 새로운 월별 parquet 데이터 파일이 업데이트가 되었는지 확인하고, 있다면 s3에 저장합니다.
-   **Geospatial Analysis**:
    -   `taxi_zones.shp` Shapefile을 사용하여 GPS 좌표(위도/경도)를 뉴욕시가 정의한 공식 택시 Zone ID로 변환합니다.

### 기술 스택 선정 이유

#### **1. API 서버: FastAPI**

본 프로젝트의 핵심인 API 서버는 Python 기반의 다른 웹 프레임워크인 Django나 Flask 대신 FastAPI를 채택했습니다. 선정 이유는 다음과 같습니다.

-   **압도적인 성능 (Performance)**
    -   **Asynchronous (비동기 처리)**: FastAPI는 ASGI(Asynchronous Server Gateway Interface)를 기반으로 만들어져 비동기 처리를 네이티브로 지원합니다. 반면, Flask와 Django는 전통적인 WSGI(Web Server Gateway Interface) 기반으로 동작하여 기본적으로 동기식으로 요청을 처리합니다. 본 프로젝트는 RDS와 DynamoDB 등 여러 데이터베이스를 동시에 조회하는 I/O-bound 작업이 많기 때문에, 비동기 처리를 통해 요청을 기다리는 동안 다른 요청을 처리할 수 있는 FastAPI가 훨씬 높은 처리량(Throughput)과 빠른 응답 속도를 보장합니다.
    -   **벤치마크**: 여러 독립적인 벤치마크에서 FastAPI는 Flask나 Django REST Framework(DRF)에 비해 월등히 높은 초당 요청 처리(RPS) 성능을 보여줍니다. 이는 수많은 택시로부터 동시에 들어오는 요청을 지연 없이 처리해야 하는 본 시스템에 필수적인 요건입니다.

-   **높은 개발 생산성 및 안정성 (Productivity & Stability)**
    -   **자동 데이터 검증**: FastAPI는 Python의 타입 힌트와 Pydantic 라이브러리를 결합하여, API로 들어오는 요청의 데이터 타입을 자동으로 검증하고 변환해줍니다. 이를 통해 개발자는 유효성 검사를 위한 별도의 코드를 작성할 필요가 없으며, 잘못된 데이터로 인한 런타임 에러를 사전에 방지할 수 있습니다. Flask나 Django에서는 이 기능을 위해 Marshmallow 같은 별도의 라이브러리를 추가로 설정해야 합니다.
    -   **자동 API 문서 생성**: 코드를 작성하는 것만으로 OpenAPI(Swagger UI)와 ReDoc 형식의 API 문서를 자동으로 생성해줍니다. 이는 프론트엔드 개발자와의 협업을 원활하게 하고, API 테스트를 매우 편리하게 만들어 개발 전체의 효율을 높입니다.

-   **경량성 및 유연성 (Lightweight & Flexibility)**
    -   **마이크로서비스에 최적화**: Django는 ORM, Admin 페이지 등 다양한 기능이 포함된 "Batteries-included" 프레임워크로, 풀스택 웹 애플리케이션에 적합합니다. 하지만 본 프로젝트처럼 특정 기능에 집중하는 API 서버(마이크로서비스)를 구축하기에는 불필요한 기능이 많아 무겁습니다. FastAPI는 API 구축에 필요한 핵심 기능에 집중한 마이크로 프레임워크이므로, 더 가볍고 유연한 구조를 가집니다.

#### **2. 데이터베이스: AWS RDS (PostgreSQL) & DynamoDB**

-   **데이터 특성에 따른 분리**: 데이터의 성격에 따라 최적의 데이터베이스를 선택했습니다. `Zone별 통계`나 `인접 Zone 목록`처럼 정형화되어 있고 변경이 적은 데이터는 관계형 데이터베이스인 **RDS (PostgreSQL)** 에 저장하여 안정적으로 관리합니다. 반면, `실시간 택시 이동 현황`처럼 읽기/쓰기가 매우 빈번하고 빠른 응답 속도가 요구되는 데이터는 NoSQL인 **DynamoDB**를 사용하여 성능과 확장성을 확보했습니다.

#### **3. 데이터 처리: AWS Lambda**

-   **서버리스 아키텍처**: 매월 한 번씩 대용량 데이터를 처리하는 파이프라인을 위해 24시간 서버를 운영하는 것은 비효율적입니다. **Lambda**를 사용하면 코드가 실행될 때만 컴퓨팅 자원을 할당하고 비용을 지불하는 서버리스 아키텍처를 구현할 수 있어, 운영 비용을 획기적으로 절감하고 인프라 관리 부담을 최소화할 수 있습니다.

## 2. 주요 기능 및 동작 원리

### 추천 로직 (`/request_place`)

1.  **위치 수신**: 택시 드라이버 앱으로부터 `taxi_id`와 현재 GPS 좌표(`lat`, `lon`)를 POST 요청으로 받습니다.
2.  **현재 Zone 식별**: 수신된 GPS 좌표를 `taxi_zones.shp` 파일과 비교하여 택시가 현재 속한 `current_zone_id`를 계산합니다.
3.  **수요 점수 계산**:
    -   `current_zone_id`에 인접한 모든 Zone을 RDS(`adjacent_zones` 테이블)에서 조회합니다.
    -   각 인접 Zone에 대해 다음 공식을 사용하여 **수요 점수(Score)** 를 계산합니다.
        > **Score** = (해당 Zone의 현재 시간대 평균 승차 수) / (현재 해당 Zone으로 이동 중인 택시 수 + 1)
    -   분모에 `+1`을 하는 이유는, 요청한 택시 자신도 해당 Zone으로 이동할 것을 가정하여 공급(택시 수)을 예측하기 위함입니다. 이는 택시가 특정 Zone에 과도하게 몰리는 것을 방지합니다.
4.  **연속 배차 최적화**:
    -   만약 해당 택시가 방금 승객을 내린 직후라면(`taxi-destination-dynamodb`에 이전 목적지 정보가 있다면), 이전 목적지로 다시 돌아가는 추천의 우선순위를 낮추는 로직이 포함되어 있습니다.
5.  **최적 Zone 반환**: 가장 높은 수요 점수를 받은 `zone_id`를 택시에게 반환합니다.
6.  **상태 업데이트**:
    -   추천된 Zone의 "이동 중인 택시 수"를 DynamoDB(`zone-count-dynamodb`)에서 1 증가시킵니다.
    -   해당 택시의 새로운 목적지를 DynamoDB(`taxi-destination-dynamodb`)에 업데이트합니다.

### 승차 완료 처리 (`/request_ride`)

1.  **승차 보고**: 택시가 추천받은 Zone 또는 다른 곳에서 승객을 태웠을 때, `taxi_id`와 함께 이 API를 호출합니다.
2.  **상태 업데이트**: 시스템은 해당 택시가 이전에 어떤 Zone으로 이동 중이었는지 확인하고, 해당 Zone의 "이동 중인 택시 수"를 1 감소시킵니다.
3.  **로깅**: 승차 발생 사실을 `log-dynamodb`에 기록합니다.

## 3. 코드 파일 설명

### `main.py`

FastAPI를 사용하여 구현된 메인 애플리케이션입니다. 서버가 시작될 때 RDS와 DynamoDB에 연결하고, 필요한 데이터를 메모리에 로드합니다. `/request_place`와 `/request_ride` 두 개의 핵심 API 엔드포인트를 제공합니다.

### `invoke_taxi_parquet_lambda.sh`

주기적으로 AWS Lambda 함수(`NYC_TLC_Crawler`)를 호출하는 셸 스크립트입니다. `last-processed-date.txt` 파일을 통해 마지막으로 처리한 데이터의 날짜를 관리하며, 매번 다음 달의 택시 운행 데이터(예: `yellow_tripdata_2025-07.parquet`)를 처리하도록 Lambda 함수에 파일명을 전달합니다. 이는 데이터 파이프라인의 일부로, RDS의 통계 데이터를 최신 상태로 유지하는 역할을 합니다.

### `load_tester.py`

`aiohttp`와 `asyncio`를 사용하여 API 서버의 성능을 테스트하는 스크립트입니다. `/request_place` 엔드포인트에 대량의 비동기 요청(기본 10,000건)을 보내 서버의 초당 요청 처리량(RPS), 성공/실패율 등을 측정합니다.

## 4. 설치 및 실행 방법

### 사전 준비

-   Python 3.12+
-   AWS 계정 및 AWS CLI 설정 (DynamoDB, RDS, Lambda 접근 권한 필요, aws cli는 설치되어 있다고 가)
-   `taxi_zones.shp` 파일 및 관련 파일들 (`.dbf`, `.shx`, `.prj` 등)
-   환경 변수 설정:
```bash
export RDS_PW="YOUR_RDS_DATABASE_PASSWORD"
```

### 의존성 설치

```bash
pip install fastapi uvicorn boto3 psycopg2-binary geopandas shapely
```

### 서버 실행

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 성능 테스트 실행

1.  `load_tester.py` 파일 내의 `BASE_URL`을 실제 서버 주소로 수정합니다.
```python
BASE_URL = "http://localhost:8000/request_place"
```
2.  스크립트를 실행합니다.
```bash
python load_tester.py
```

### 데이터 파이프라인 실행

1.  AWS CLI가 올바르게 설정되었는지 확인합니다.
2.  스크립트에 실행 권한을 부여하고 실행합니다.
```bash
chmod +x invoke_taxi_parquet_lambda.sh
./invoke_taxi_parquet_lambda.sh
```
