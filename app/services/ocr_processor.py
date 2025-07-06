from typing import Dict
from fastapi import UploadFile
from services.factory import get_ocr_service
from services.ocr.gemini import GeminiOCRService
from services.ocr.textract import TextractOCRService
from services.utils.logger import get_logger
from services.utils import postprocess_fields


class OCRProcessor:
    """Coordinates OCR extraction."""

    def __init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__)
        self.ocr_service = get_ocr_service()
        self.refiner: GeminiOCRService | None = None
        try:
            is_gemini = isinstance(self.ocr_service, GeminiOCRService)
        except TypeError:  # when patched with non-type
            is_gemini = False
        if not is_gemini:
            self.refiner = GeminiOCRService()

    async def analyze(self, file: UploadFile) -> Dict:
        """Analyze a file and return the extracted fields."""
        self.logger.info("Starting analysis for %s", file.filename)
        raw = await self.ocr_service.analyze(file)
        cleaned = postprocess_fields(raw.fields)
        if self.refiner:
            refined = await self.refiner.refine(cleaned)
            return {"form_type": refined.form_name, "fields": refined.fields}
        return {"form_type": raw.form_name, "fields": cleaned}

