# services/ocr/textract/aws_service.py
import os
import asyncio
import magic
from typing import Dict
from fastapi import UploadFile
from services.utils.logger import get_logger

from .ocr_textract import OcrTextract
from .textract_block_parser import TextractBlockParser
from .s3_uploader import S3Uploader

AWS_REGION = os.getenv("AWS_REGION", "us-east-2")
AWS_BUCKET = os.getenv("AWS_BUCKET", "ocr-bucket-pbt-devop")
MAX_RETRIES = int(os.getenv("TEXTRACT_MAX_RETRIES", 30))
SLEEP_TIME = int(os.getenv("TEXTRACT_SLEEP_SECONDS", 4))

class AWSTextractOCRService:
    def __init__(self, region_name: str = AWS_REGION, bucket_name: str = AWS_BUCKET):
        self.logger = get_logger(self.__class__.__name__)
        self.textract = OcrTextract(region_name=region_name)
        self.parser = TextractBlockParser()
        self.s3 = S3Uploader(bucket_name, region_name=region_name)
        self.bucket = bucket_name

    async def wait_for_textract_result(self, get_result_fn, job_id: str, max_retries: int = 30, delay: int = 4):
        for attempt in range(max_retries):
            result = await asyncio.to_thread(get_result_fn, job_id)
            status = result.get("JobStatus", "UNKNOWN")
            self.logger.info("Attempt %s/%s – Status: %s", attempt + 1, max_retries, status)
            if status == "SUCCEEDED":
                return result
            if status == "FAILED":
                raise RuntimeError(f"Textract job failed with status: {status}")
            await asyncio.sleep(delay)
        raise TimeoutError("Textract job did not complete in time.")

    async def analyze(self, file: UploadFile) -> Dict:
        self.logger.info("Analyzing file: %s", file.filename)
        contents = await file.read()
        mime_type = magic.from_buffer(contents, mime=True)
        is_pdf = mime_type == "application/pdf"

        try:
            if is_pdf:
                s3_key = f"uploads/{file.filename}"
                self.logger.info("Uploading %s to S3 bucket %s", s3_key, self.bucket)
                await asyncio.to_thread(self.s3.upload, s3_key, contents)
                self.logger.info("Starting Textract job")
                job_id = await asyncio.to_thread(self.textract.start_document_analysis, self.bucket, s3_key)
                result = await self.wait_for_textract_result(self.textract.get_document_analysis, job_id, MAX_RETRIES, SLEEP_TIME)
                await asyncio.to_thread(self.s3.delete, s3_key)
                blocks = result.get("Blocks", []) if result else []
            else:
                result = await asyncio.to_thread(self.textract.analyze_document, contents)
                blocks = result.get("Blocks", [])
        except Exception as exc:
            self.logger.error("Error during Textract processing: %s", exc)
            raise

        self.logger.info("Parsing Textract blocks")
        fields = self.parser.parse(blocks)
        self.logger.info("Fields extracted: %s", len(fields))
        return {"fields": fields}