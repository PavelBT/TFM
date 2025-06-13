# Ruta: services/storage/s3_uploader.py

import boto3

class S3Uploader:
    def __init__(self, bucket: str, region: str = "us-east-2"):
        self.bucket = bucket
        self.s3 = boto3.client("s3", region_name=region)

    def upload_file(self, content: bytes, s3_key: str) -> None:
        self.s3.put_object(Bucket=self.bucket, Key=s3_key, Body=content)

    def delete_file(self, s3_key: str) -> None:
        self.s3.delete_object(Bucket=self.bucket, Key=s3_key)
