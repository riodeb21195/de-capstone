from pathlib import Path
from datetime import datetime, timezone

import boto3
from botocore.client import Config

from config import(
    MINIO_ENDPOINT,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_BUCKET,
)
from extract import extract, save_raw

def get_minio_client():
    return boto3.client(
        's3',
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        config=Config(signature_version='s3v4'),
        region_name='us-east-1',
    )

def ensure_bucket(client, bucket_name: str):
    existing_buckets = [b['Name'] for b in client.list_buckets()['Buckets']]
    if bucket_name not in existing_buckets:
        print(f"[ingest] Bucket '{bucket_name}' erstellt")
    else:
        print(f"[ingest] Bucket '{bucket_name}' existiert bereits")

def upload_file(client, bucket_name: str, local_path: Path, object_key: str):
    client.upload_file(str(local_path), bucket_name, object_key)
    print(f"[ingest] Hochgeladen: {local_path} -> s3://{bucket_name}/{object_key}")

def main():
    data = extract()
    local_path = save_raw(data)

    client = get_minio_client()
    ensure_bucket(client, MINIO_BUCKET)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    object_key = f"raw/opensky/{today}/{local_path.name}"

    upload_file(client, MINIO_BUCKET, local_path, object_key)


if __name__ == "__main__":
    main()