import boto3


class S3Uploader:
    def __init__(self, bucket: str, region_name: str = "us-east-2"):
        self.bucket = bucket
        self.client = boto3.client("s3", region_name=region_name)

    def upload(self, key: str, data: bytes) -> None:
        self.client.put_object(Bucket=self.bucket, Key=key, Body=data)

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)
