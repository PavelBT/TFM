from typing import Dict
from fastapi import UploadFile
from services.factory import get_ocr_service
from services.utils.logger import get_logger


class OCRProcessor:
    """Coordinates OCR extraction."""

    def __init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__)
        self.ocr_service = get_ocr_service()

    async def analyze(self, file: UploadFile) -> Dict:
        """Analyze a file and return the extracted fields."""
        self.logger.info("Starting analysis for %s", file.filename)
        raw = await self.ocr_service.analyze(file)
        return {"form_type": raw.form_name, "fields": raw.fields}

