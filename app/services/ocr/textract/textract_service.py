# services/ocr/textract/textract_service.py
import os
import asyncio
from uuid import uuid4
from fastapi import UploadFile
from interfaces.ocr_service import OCRService
from models import OCRResponse
from services.utils.logger import get_logger
from trp import Document
import boto3


class TextractOCRService(OCRService):
    """Extract fields using Amazon Textract."""

    def __init__(self, region: str | None = None, bucket: str | None = None) -> None:
        self.logger = get_logger(self.__class__.__name__)
        region = region or os.getenv("AWS_REGION")
        self.bucket = bucket or os.getenv("S3_BUCKET", "")
        self.client = boto3.client("textract", region_name=region)
        self.s3 = boto3.client("s3", region_name=region)

    async def analyze(self, file: UploadFile) -> OCRResponse:
        self.logger.info("Analyzing file with Textract: %s", file.filename)
        data = await file.read()
        if file.content_type == "application/pdf" or file.filename.lower().endswith(".pdf"):
            if not self.bucket:
                raise RuntimeError("S3_BUCKET not configured")

            key = f"tmp/{uuid4()}-{file.filename}"
            await asyncio.to_thread(
                self.s3.put_object,
                Bucket=self.bucket,
                Key=key,
                Body=data,
            )

            try:
                job = await asyncio.to_thread(
                    self.client.start_document_analysis,
                    DocumentLocation={"S3Object": {"Bucket": self.bucket, "Name": key}},
                    FeatureTypes=["FORMS"],
                )
                job_id = job["JobId"]

                pages: list[dict] = []
                while True:
                    result = await asyncio.to_thread(
                        self.client.get_document_analysis, JobId=job_id
                    )
                    status = result.get("JobStatus")
                    if status in {"SUCCEEDED", "FAILED"}:
                        pages.append(result)
                        break
                    await asyncio.sleep(0.5)

                next_token = result.get("NextToken")
                while next_token:
                    res = await asyncio.to_thread(
                        self.client.get_document_analysis,
                        JobId=job_id,
                        NextToken=next_token,
                    )
                    pages.append(res)
                    next_token = res.get("NextToken")

                response = {"Blocks": []}
                for page in pages:
                    response["Blocks"].extend(page.get("Blocks", []))
            finally:
                await asyncio.to_thread(
                    self.s3.delete_object, Bucket=self.bucket, Key=key
                )
        else:
            response = await asyncio.to_thread(
                self.client.analyze_document,
                Document={"Bytes": data},
                FeatureTypes=["FORMS"],
            )

        doc = Document(response)
        fields: dict[str, str] = {}
        for page in doc.pages:
            for field in page.form.fields:
                key = getattr(field.key, "text", "")
                value = getattr(field.value, "text", "")
                if key:
                    fields[key] = value

        return OCRResponse(form_name="", fields=fields)
