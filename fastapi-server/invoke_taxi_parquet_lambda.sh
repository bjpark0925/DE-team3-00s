#!/bin/bash

# 설정 변수
FUNCTION_NAME="NYC_TLC_Crawler"
REGION="ap-northeast-2"
OUTPUT_FILE="/tmp/lambda-response.json"

STATE_FILE="last-processed-date.txt"
FILE_PREFIX="yellow_tripdata_"
FILE_SUFFIX=".parquet"

# --- 상태 파일 존재 여부 확인 및 초기값 설정 ---
if [ ! -f "$STATE_FILE" ]; then
    echo "State file not found. Creating with initial date: 2025-06"
    echo "2025-06" > "$STATE_FILE"
fi

# --- 마지막으로 처리된 날짜를 읽고 다음 달 날짜 계산 ---
LAST_PROCESSED_DATE=$(cat "$STATE_FILE")
echo "Last processed date: $LAST_PROCESSED_DATE"

# 다음 달 계산 (Linux 'date' 명령 사용)
NEXT_DATE=$(date -d "$LAST_PROCESSED_DATE-01 +1 month" "+%Y-%m")
echo "Next date to process: $NEXT_DATE"

DYNAMIC_FILENAME="${FILE_PREFIX}${NEXT_DATE}${FILE_SUFFIX}"
echo $DYNAMIC_FILENAME
PAYLOAD='{"filename": "'"$DYNAMIC_FILENAME"'"}'

# --- 명령어 실행 ---
echo "Invoking Lambda function: $FUNCTION_NAME at $(date)"

# aws cli 명령어를 실행하고 결과 저장
aws lambda invoke \
    --function-name "$FUNCTION_NAME" \
    --region "$REGION" \
    --payload "$PAYLOAD" \
    --cli-binary-format raw-in-base64-out \
    "$OUTPUT_FILE"

STATUS_CODE=$(jq -r '.statusCode' "$OUTPUT_FILE")
BODY_MESSAGE=$(jq -r '.body' "$OUTPUT_FILE")

# statusCode 값에 따라 성공/실패 여부 판단
if [ "$STATUS_CODE" -eq 200 ]; then
    echo "SUCCESS: Lambda function executed successfully."
    echo "Response body: $BODY_MESSAGE"
    # 성공 시에만 상태 파일 업데이트 (날짜 부분만 저장)
    echo "$NEXT_DATE" > "$STATE_FILE"
    echo "State file updated to: $NEXT_DATE"

else
    echo "FAILURE: Lambda function returned an error."
    echo "Status Code: $STATUS_CODE"
    echo "Error message: $BODY_MESSAGE"
fi

echo "Script finished."
