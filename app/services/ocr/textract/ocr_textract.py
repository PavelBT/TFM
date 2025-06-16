import boto3
from typing import Dict


class OcrTextract:
    def __init__(self, region_name: str = "us-east-2"):
        self.client = boto3.client("textract", region_name=region_name)

    def analyze_document(self, document_bytes: bytes) -> Dict:
        return self.client.analyze_document(
            Document={"Bytes": document_bytes},
            FeatureTypes=["FORMS"],
        )

    def start_document_analysis(self, bucket: str, key: str) -> str:
        response = self.client.start_document_analysis(
            DocumentLocation={"S3Object": {"Bucket": bucket, "Name": key}},
            FeatureTypes=["FORMS"],
        )
        return response["JobId"]

    def get_document_analysis(self, job_id: str) -> Dict:
        return self.client.get_document_analysis(JobId=job_id)
