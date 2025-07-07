from typing import Dict
from fastapi import UploadFile
from services.factory import get_ocr_service
from services.ocr.gemini import GeminiOCRService, GeminiRefinerService
from services.utils.logger import get_logger
from services.utils import postprocess_fields


class OCRProcessor:
    """Coordinates OCR extraction.

    This class temporarily allows overriding the OCR backend and the
    refiner usage via parameters instead of relying solely on environment
    variables. Environment variables remain supported and unchanged.
    """

    def __init__(self, service_name: str | None = None, use_refiner: bool | None = None) -> None:
        self.logger = get_logger(self.__class__.__name__)
        self.ocr_service = get_ocr_service(service_name)
        self.refiner: GeminiRefinerService | None = None

        if use_refiner is None:
            # Default behaviour: use refiner only when OCR service is not Gemini
            try:
                is_gemini = isinstance(self.ocr_service, GeminiOCRService)
            except TypeError:  # when patched with non-type
                is_gemini = False
            if not is_gemini:
                self.refiner = GeminiRefinerService()
        elif use_refiner:
            self.refiner = GeminiRefinerService()

    async def analyze(self, file: UploadFile) -> Dict:
        """Analyze a file and return the extracted fields."""
        self.logger.info("Starting analysis for %s", file.filename)
        raw = await self.ocr_service.analyze(file)
        cleaned = postprocess_fields(raw.fields)
        if self.refiner:
            refined = await self.refiner.refine(cleaned)
            return {"form_type": refined.form_name, "fields": refined.fields}
        return {"form_type": raw.form_name, "fields": cleaned}

