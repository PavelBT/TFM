import asyncio
import magic
from typing import Dict
from fastapi import UploadFile

from .ocr_textract import OcrTextract
from .textract_block_parser import TextractBlockParser
from .s3_uploader import S3Uploader


class AWSTextractOCRService:
    def __init__(self, region_name: str = "us-east-2", bucket_name: str = "ocr-bucket"):
        self.textract = OcrTextract(region_name=region_name)
        self.parser = TextractBlockParser()
        self.s3 = S3Uploader(bucket_name, region_name=region_name)
        self.bucket = bucket_name

    async def analyze(self, file: UploadFile) -> Dict:
        contents = await file.read()
        mime_type = magic.from_buffer(contents, mime=True)
        is_pdf = mime_type == "application/pdf"

        if is_pdf:
            s3_key = f"uploads/{file.filename}"
            await asyncio.to_thread(self.s3.upload, s3_key, contents)
            job_id = await asyncio.to_thread(self.textract.start_document_analysis, self.bucket, s3_key)
            status = "IN_PROGRESS"
            tries = 0
            result = None
            while status == "IN_PROGRESS" and tries < 20:
                await asyncio.sleep(3)
                result = await asyncio.to_thread(self.textract.get_document_analysis, job_id)
                status = result["JobStatus"]
                tries += 1
            await asyncio.to_thread(self.s3.delete, s3_key)
            if status != "SUCCEEDED":
                raise RuntimeError(f"Textract job failed with status: {status}")
            blocks = result.get("Blocks", []) if result else []
        else:
            result = await asyncio.to_thread(self.textract.analyze_document, contents)
            blocks = result.get("Blocks", [])

        fields = self.parser.parse(blocks)
        return {"fields": fields}
