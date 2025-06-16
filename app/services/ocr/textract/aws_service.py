import os
import asyncio
import magic
from typing import Dict
from fastapi import UploadFile
import logging

from .ocr_textract import OcrTextract
from .textract_block_parser import TextractBlockParser
from .s3_uploader import S3Uploader

AWS_REGION = os.getenv("AWS_REGION", "us-east-2")
AWS_BUCKET = os.getenv("AWS_BUCKET", "ocr-bucket-pbt-devop")

logger = logging.getLogger(__name__)


class AWSTextractOCRService:
    def __init__(self, region_name: str = AWS_REGION, bucket_name: str = AWS_BUCKET):
        self.textract = OcrTextract(region_name=region_name)
        self.parser = TextractBlockParser()
        self.s3 = S3Uploader(bucket_name, region_name=region_name)
        self.bucket = bucket_name

    async def analyze(self, file: UploadFile) -> Dict:
        """Analyze a document using AWS Textract."""
        try:
            logger.info("Starting analysis of '%s'", file.filename)
            contents = await file.read()
            mime_type = magic.from_buffer(contents, mime=True)
            logger.info("Detected mime type: %s", mime_type)
            is_pdf = mime_type == "application/pdf"

            if is_pdf:
                logger.info("Uploading PDF to S3 bucket '%s'", self.bucket)
                s3_key = f"uploads/{file.filename}"
                await asyncio.to_thread(self.s3.upload, s3_key, contents)
                logger.info("Starting asynchronous Textract job")
                job_id = await asyncio.to_thread(
                    self.textract.start_document_analysis, self.bucket, s3_key
                )
                status = "IN_PROGRESS"
                tries = 0
                result = None
                while status == "IN_PROGRESS" and tries < 20:
                    await asyncio.sleep(3)
                    result = await asyncio.to_thread(
                        self.textract.get_document_analysis, job_id
                    )
                    status = result["JobStatus"]
                    logger.info("Textract job status: %s", status)
                    tries += 1
                logger.info("Cleaning up temporary file from S3")
                await asyncio.to_thread(self.s3.delete, s3_key)
                if status != "SUCCEEDED":
                    logger.error("Textract job failed with status: %s", status)
                    raise RuntimeError(f"Textract job failed with status: {status}")
                logger.info("Textract job completed successfully")
                blocks = result.get("Blocks", []) if result else []
            else:
                logger.info("Using synchronous Textract API")
                result = await asyncio.to_thread(self.textract.analyze_document, contents)
                blocks = result.get("Blocks", [])

            logger.info("Parsing Textract response")
            fields = self.parser.parse(blocks)
            logger.info("Parsed %d fields", len(fields))
            return {"fields": fields}
        except Exception as e:
            logger.exception("Error during Textract analysis")
            raise
