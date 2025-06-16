from typing import Dict
from fastapi import UploadFile
from services.factory import get_ocr_service
from services.postprocessors.postprocessor_factory import get_postprocessor
from services.ai_refiners.factory import get_ai_refiner
from services.ocr.form_identifier import FormIdentifier
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
        form_type = FormIdentifier.identify(raw["fields"])

        self.logger.info("Identified form type: %s", form_type)
        postprocessor = get_postprocessor(form_type=form_type)
        processed = postprocessor.process(raw["fields"])

        refined = {}
        if self.refiner_type:
            try:
                refiner_service = get_ai_refiner(self.refiner_type)
                refined = refiner_service.refine(fields=processed)
            except Exception as exc:
                self.logger.warning("Refinement failed: %s", exc)

        return {"form_type": form_type, "fields": refined | processed}

    def refiner(self, fields: Dict,refiner_type: str | None = None):
        """Get the AI refiner for the specified type."""
        if not self.refiner_type:
            return fields

        for section, content in fields.items():
            try:
                result = self.refiner.refine({section: content})
                if isinstance(content, dict):
                    if isinstance(result, dict) and result:
                        fields[section] = next(iter(result.values()))
                else:
                    if isinstance(result, dict) and section in result:
                        fields[section] = result[section]
            except Exception:
                # if refinement fails keep original
                fields[section] = content
