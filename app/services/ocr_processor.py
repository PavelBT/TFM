from typing import Dict
from fastapi import UploadFile
from services.factory import get_ocr_service
from services.postprocessors.postprocessor_factory import get_postprocessor
from services.ai_refiners.factory import get_ai_refiner
from services.ocr.form_identifier import FormIdentifier
import logging


logger = logging.getLogger(__name__)


class OCRProcessor:
    """Coordinates OCR extraction and postprocessing."""

    def __init__(self, service_name: str = "aws", refiner_type: str | None = None):
        self.ocr_service = get_ocr_service(service_name)
        self.refiner_type = refiner_type

    async def analyze(self, file: UploadFile) -> Dict:
        """Run OCR, postprocessing and optional refinement."""
        logger.info("Running OCR service")
        try:
            raw = await self.ocr_service.analyze(file)
        except Exception as e:
            logger.error("Error during OCR service execution: %s", e)
            raise

        form_type = FormIdentifier.identify(raw["fields"])
        logger.info("Identified form type: %s", form_type)

        # postprocessor: clean and structure the fields
        postprocessor = get_postprocessor(form_type=form_type)
        logger.info("Postprocessing fields")
        processed = postprocessor.process(raw["fields"])

        # refiner
        refined = {}
        if self.refiner_type:
            logger.info("Refining fields using %s", self.refiner_type)
            refiner_service = get_ai_refiner(self.refiner_type)
            refined = refiner_service.refine(fields=processed)

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