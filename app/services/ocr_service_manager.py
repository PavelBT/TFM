# app/services/ocr_service_manager.py
from typing import Dict
import logging
from fastapi import UploadFile
from services.factory import get_ocr_service
from services.field_correctors.structured_cleaner import StructuredFieldCorrector
from services.ai_refiners.factory import get_ai_refiner


class OCRServiceManager:
    """Coordinador que ejecuta OCR, limpieza estructurada y refinamiento opcional."""

    def __init__(self, service_name: str = "aws", refiner_type: str | None = None):
        self.ocr_service = get_ocr_service(service_name)
        self.cleaner = StructuredFieldCorrector()
        self.refiner = get_ai_refiner(refiner_type)

    async def analyze(self, file: UploadFile) -> Dict:
        raw = await self.ocr_service.analyze(file)
        structured = self.cleaner.transform(raw["fields"])

        if not self.refiner:
            return {"fields": structured}

        for section, content in structured.items():
            try:
                result = self.refiner.refine({section: content})
                if isinstance(content, dict):
                    if isinstance(result, dict) and result:
                        structured[section] = next(iter(result.values()))
                else:
                    if isinstance(result, dict) and section in result:
                        structured[section] = result[section]
            except Exception as e:
                logging.warning(f"[OCRServiceManager] Error al refinar sección '{section}': {e}")
        return {"fields": structured}
