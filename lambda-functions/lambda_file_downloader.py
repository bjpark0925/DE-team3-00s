import subprocess
import json
import os

import requests
import boto3
from boto3.s3.transfer import S3UploadFailedError


# send the failover message to slack
def send_slack_message(message):
    webhook_url = "your-webhook-url"
    headers = {'Content-Type': 'application/json'}
    payload = {'text': message}
    response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
    return response.status_code == 200


def lambda_handler(event, context):
    s3 = boto3.client('s3')
    url = "your-url"
    filename = event['filename']
    local_filename = "/tmp/" + filename
    bucket_name = "your-bucket-name"
    key_name = f"nyc_taxi/{filename}"

    try:
        subprocess.run(["curl", "-o", local_filename, url + filename], check=True)
    except subprocess.CalledProcessError as e:
        send_slack_message(f"Error downloading file: {e}")
        return {
            'statusCode': 500,
            'body': f"Error downloading file: {e}"
        }

    try:
        s3.upload_file(local_filename, bucket_name, key_name)
    except S3UploadFailedError as e:
        send_slack_message(f"Error uploading file to S3: {e}")
        return {
            'statusCode': 500,
            'body': f"Error uploading file to S3: {e}"
        }

    # check file size to upload normal files only
    file_size = os.path.getsize(local_filename)

    if file_size < 500:
        error_message = f"File size ({file_size} bytes) is less than 500 bytes. Aborting upload."
        send_slack_message(error_message)
        return {
            'statusCode': 400,
            'body': error_message
        }

    send_slack_message(f"Successfully uploaded file: {filename}")
    return {
        'statusCode': 200,
        'body': f"File {filename} uploaded to s3://{bucket_name}/{key_name}"
    }