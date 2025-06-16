from typing import Dict
from fastapi import UploadFile
from services.factory import get_ocr_service
from services.postprocessors.postprocessor_factory import get_postprocessor
from services.ocr.form_identifier import FormIdentifier


class OCRProcessor:
    """Coordinates OCR extraction and postprocessing."""

    def __init__(self, service_name: str = "aws", refiner_type: str | None = None):
        self.ocr_service = get_ocr_service(service_name)
        self.postprocessor = get_postprocessor(structured=True, refiner_type=refiner_type)

    async def analyze(self, file: UploadFile) -> Dict:
        raw = await self.ocr_service.analyze(file)
        processed = self.postprocessor.process(raw["fields"])
        form_type = FormIdentifier.identify(raw["fields"])
        return {"form_type": form_type, "fields": processed}
