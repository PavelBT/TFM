from typing import Dict
from fastapi import UploadFile
from services.factory import get_ocr_service
from services.postprocessors.postprocessor_factory import get_postprocessor
from services.ai_refiners.factory import get_ai_refiner
from services.utils.logger import get_logger


class OCRProcessor:
    """Coordinates OCR extraction and postprocessing."""

    def __init__(self, service_name: str = "aws", refiner_type: str | None = None):
        self.logger = get_logger(self.__class__.__name__)
        self.ocr_service = get_ocr_service(service_name)
        self.refiner_type = refiner_type

    async def analyze(self, file: UploadFile) -> Dict:
        self.logger.info("Starting analysis for %s", file.filename)
        raw = await self.ocr_service.analyze(file)
        form_type = raw.form_name

        self.logger.info("Identified form type: %s", form_type)
        postprocessor = get_postprocessor(form_type=form_type)
        processed = postprocessor.process(raw.fields)

        refined = {}
        self.refiner_type = None ### borrar
        if self.refiner_type:
            try:
                refiner_service = get_ai_refiner(self.refiner_type)
                refined = refiner_service.refine(fields=processed)
            except Exception as exc:
                self.logger.warning("Refinement failed: %s", exc)

        fields = refined if refined else processed
        return {"form_type": form_type, "fields": fields}

