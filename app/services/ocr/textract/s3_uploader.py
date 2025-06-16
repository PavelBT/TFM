import boto3
import logging


logger = logging.getLogger(__name__)


class S3Uploader:
    def __init__(self, bucket: str, region_name: str = "us-east-2"):
        self.bucket = bucket
        self.client = boto3.client("s3", region_name=region_name)

    def upload(self, key: str, data: bytes) -> None:
        try:
            logger.info("Uploading '%s' to bucket '%s'", key, self.bucket)
            self.client.put_object(Bucket=self.bucket, Key=key, Body=data)
        except Exception:
            logger.exception("Failed to upload '%s'", key)
            raise

    def delete(self, key: str) -> None:
        try:
            logger.info("Deleting '%s' from bucket '%s'", key, self.bucket)
            self.client.delete_object(Bucket=self.bucket, Key=key)
        except Exception:
            logger.exception("Failed to delete '%s'", key)
            raise
