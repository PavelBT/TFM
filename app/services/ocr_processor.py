from typing import Dict
from fastapi import UploadFile
from services.factory import get_ocr_service
from services.ocr.gemini import GeminiOCRService, GeminiRefinerService
from services.utils.logger import get_logger
from services.utils import postprocess_fields


class OCRProcessor:
    """Coordinates OCR extraction."""

    def __init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__)
        # Service and refiner are selected per request. This allows
        # temporary runtime configuration while comparing OCR engines.

    async def analyze(
        self,
        file: UploadFile,
        ocr_service: str | None = None,
        use_refiner: bool | None = None,
    ) -> Dict:
        """Analyze a file and return the extracted fields.

        Parameters are optional and override environment defaults. This is
        temporary code used during the OCR comparison phase.
        """

        self.logger.info("Starting analysis for %s", file.filename)

        service = get_ocr_service(ocr_service)
        is_gemini = isinstance(service, GeminiOCRService)

        if use_refiner is None:
            use_refiner = not is_gemini

        refiner: GeminiRefinerService | None = None
        if use_refiner and not is_gemini:
            refiner = GeminiRefinerService()

        raw = await service.analyze(file)
        cleaned = postprocess_fields(raw.fields)

        if refiner:
            self.logger.info("Starting refiner for %s", file.filename)
            refined = await refiner.refine(cleaned)
            return {"form_type": refined.form_name, "fields": refined.fields}

        return {"form_type": raw.form_name, "fields": cleaned}

