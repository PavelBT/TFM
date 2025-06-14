# app/services/aws_textract.py
from typing import Dict
from fastapi import UploadFile
from app.interfaces.ocr_service import OCRService
from app.services.ocr.textract.client import TextractClient
from app.services.ocr.textract.extractor import TextractExtractor


class AWSTextractOCRService(OCRService):
    def __init__(self, region_name: str = "us-east-2", bucket_name: str = "ocr-bucket-pbt-devop"):
        self.client = TextractClient(region_name=region_name, bucket_name=bucket_name)
        self.extractor = TextractExtractor()

    async def analyze(self, file: UploadFile) -> Dict:
        blocks = await self.client.analyze(file)
        fields = self.extractor.extract_fields(blocks)
        return {"fields": fields}

