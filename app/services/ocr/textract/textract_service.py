# services/ocr/textract/textract_service.py
import os
import asyncio
from fastapi import UploadFile
from interfaces.ocr_service import OCRService
from models import OCRResponse
from services.utils.logger import get_logger
from trp import Document
import boto3


class TextractOCRService(OCRService):
    """Extract fields using Amazon Textract."""

    def __init__(self, region: str | None = None) -> None:
        self.logger = get_logger(self.__class__.__name__)
        region = region or os.getenv("AWS_REGION")
        self.client = boto3.client("textract", region_name=region)

    async def analyze(self, file: UploadFile) -> OCRResponse:
        self.logger.info("Analyzing file with Textract: %s", file.filename)
        data = await file.read()
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
