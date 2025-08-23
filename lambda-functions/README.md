# NYC TLC 운행 데이터 파일을 자동 다운로드하는 AWS Lambda Function

## 1. 개요

지정된 URL로부터 파일을 다운로드하여 AWS S3 버킷에 업로드하는 단일 AWS Lambda 함수입니다.

주기적으로 생성되는 데이터 파일(예: NYC Taxi 월간 데이터)을 안정적으로 수집하여 데이터 레이크의 역할을 하는 S3 버킷에 저장하기 위해 설계되었습니다. 작업의 성공 또는 실패 여부는 Slack을 통해 실시간으로 통보받을 수 있습니다.

매달 한 달 동안의 데이터가 parquet 파일로 업로드 되지만, 몇 일에 업로드가 되는지는 일정하지 않아 cron을 통해 매일 한 번 씩 파일을 요청합니다.

## 2. 주요 기능 및 동작 순서

1.  **트리거**: Lambda 함수는 `filename`을 포함하는 JSON 이벤트를 통해 트리거됩니다.
2.  **파일 다운로드**: 외부 URL과 이벤트로 전달받은 `filename`을 조합하여 전체 파일 경로를 생성합니다. `curl` 명령어를 사용하여 해당 파일을 Lambda의 임시 저장 공간인 `/tmp/` 디렉토리에 다운로드합니다.
3.  **S3 업로드**: 다운로드된 파일을 지정된 S3 버킷의 특정 경로(`nyc_taxi/`)에 업로드합니다.
4.  **유효성 검증**: 업로드된 파일의 크기를 확인합니다. 파일 크기가 500바이트 미만일 경우, 정상적인 데이터가 아닌 오류 페이지 다운로드된 것으로 간주하고 작업을 실패 처리합니다.
5.  **결과 통보**: 모든 작업의 최종 성공 또는 실패 결과를 Slack 웹훅(Webhook)을 통해 지정된 채널로 전송하여 관리자가 즉시 상황을 인지할 수 있도록 합니다.

## 3. 설정 및 배포

이 Lambda 함수를 배포하고 사용하기 위해서는 다음 설정이 필요합니다.

### 코드 수정 사항

배포 전, 코드 내의 다음 변수들을 실제 환경에 맞게 수정해야 합니다.

-   `send_slack_message` 함수 내의 `webhook_url`: Slack 알림을 수신할 채널의 Webhook URL
-   `lambda_handler` 함수 내의 `url`: 다운로드할 파일이 위치한 기본 URL
-   `lambda_handler` 함수 내의 `bucket_name`: 파일을 업로드할 S3 버킷 이름

> **권장 사항**: 보안을 위해 위 값들을 코드에 하드코딩하는 대신, Lambda 함수의 **환경 변수(Environment Variables)** 로 설정하여 사용하는 것이 좋습니다.

### IAM 권한 (IAM Permissions)

이 Lambda 함수가 실행될 IAM 역할(Role)에는 최소한 다음 권한이 필요합니다.

-   **Amazon S3**: S3 버킷에 파일을 업로드하기 위한 `s3:PutObject` 권한
-   **LambdaBasicExecutionRole**: Lambda 함수가 실행되기 위한 기본적인 권한

### Lambda 함수 설정

-   **핸들러(Handler)**: `lambda_file_downloader.lambda_handler`
-   **런타임(Runtime)**: `Python 3.13` 이상
-   **메모리(Memory)**: `128MB` (기본값으로 충분)
-   **제한 시간(Timeout)**: 다운로드 및 업로드 시간을 고려하여 충분히 길게 설정해야 합니다. 평균 다운로드 시간이 30~40초가 소요되었으므로 1분으로 두었습니다.
-   **의존성(Dependencies)**:
    -   이 함수는 `requests` 라이브러리를 사용합니다. AWS Lambda Python 런타임에는 이 라이브러리가 기본적으로 포함되어 있지 않으므로 `requests` 라이브러리가 담긴 layer를 만들었습니다.
    -   `boto3`는 Lambda 런타임에 기본 포함되어 있으므로 별도로 추가할 필요가 없습니다.

## 4. 사용 방법

### 함수 호출

AWS SDK, AWS CLI 또는 다른 AWS 서비스(예: EventBridge 스케줄러)를 통해 Lambda 함수를 호출할 수 있습니다.

저희는 API Server 내에서 cronjob으로 하루에 한 번씩 0시 0분에 (KST 오전 9시 0분) invoke하도록 설정했습니다.

### 입력 이벤트 (Input Event)

함수를 호출할 때 다음과 같은 JSON 형식의 이벤트를 전달해야 합니다.

```json
{ "filename": "yellow_tripdata_2025-08.parquet" }
```

### 응답 (Response)

-   **성공 시 (Status Code: 200)**:
    ```json
    { "statusCode": 200, "body": "File yellow_tripdata_2025-08.parquet uploaded to s3://your-bucket-name/nyc_taxi/yellow_tripdata_2025-08.parquet" }
    ```

-   **실패 시 (Status Code: 400 or 500)**:
    ```json
    { "statusCode": 500, "body": "Error downloading file: ..." }
    ```
