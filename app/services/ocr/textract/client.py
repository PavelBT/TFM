import boto3
import magic
import json
import time
from pathlib import Path
from typing import List
from fastapi import UploadFile


class TextractClient:
    def __init__(self, region_name: str = "us-east-2", bucket_name: str = "ocr-bucket-pbt-devop"):
        self.client = boto3.client("textract", region_name=region_name)
        self.s3 = boto3.client("s3", region_name=region_name)
        self.bucket = bucket_name

        dataset_path = Path(__file__).resolve().parents[2] / "training" / "textract_adapter_dataset.jsonl"
        queries = []
        try:
            with open(dataset_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    data = json.loads(line)
                    queries.extend(data.get("queries", []))
        except FileNotFoundError:
            queries = []

        self.queries = queries

    async def analyze(self, file: UploadFile) -> List[dict]:
        contents = await file.read()
        mime_type = magic.from_buffer(contents, mime=True)
        is_pdf = mime_type == "application/pdf"

        if is_pdf:
            s3_key = f"uploads/{file.filename}"
            self.s3.put_object(Bucket=self.bucket, Key=s3_key, Body=contents)

            start_response = self.client.start_document_analysis(
                DocumentLocation={"S3Object": {"Bucket": self.bucket, "Name": s3_key}},
                FeatureTypes=["FORMS", "QUERIES"],
                QueriesConfig={"Queries": self.queries}
            )
            job_id = start_response["JobId"]

            status = "IN_PROGRESS"
            tries = 0
            while status == "IN_PROGRESS" and tries < 20:
                time.sleep(3)
                result = self.client.get_document_analysis(JobId=job_id)
                status = result["JobStatus"]
                tries += 1

            if status != "SUCCEEDED":
                raise RuntimeError(f"Textract job failed with status: {status}")

            blocks = result.get("Blocks", [])
            self.s3.delete_object(Bucket=self.bucket, Key=s3_key)
            return blocks
        else:
            result = self.client.analyze_document(
                Document={"Bytes": contents},
                FeatureTypes=["FORMS", "QUERIES"],
                QueriesConfig={"Queries": self.queries}
            )
            return result.get("Blocks", [])

