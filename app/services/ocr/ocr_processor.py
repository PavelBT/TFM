from fastapi import UploadFile
import os
from models.data_response import DataResponse
from services.ocr.factory import get_ocr_service
from services.ocr.textract.ocrtextract import OcrTextract

class OCRProcessor:
    """Orchestrates OCR extraction and post-processing."""

    def __init__(self, service_name: str | None = None, refiner_type: str | None = None):
        self.service_name = service_name or os.getenv("OCR_SERVICE", "aws")
        self.refiner_type = refiner_type or os.getenv("REFINER_TYPE", "gpt")
        self.service = get_ocr_service(self.service_name)

    async def process(self, file: UploadFile) -> DataResponse:
        if self.service_name == "aws":
            pipeline = OcrTextract(self.service, refiner_type=self.refiner_type)
            return await pipeline.process(file)
        else:
            raise NotImplementedError(
                f"OCR service '{self.service_name}' is not supported"
            )
