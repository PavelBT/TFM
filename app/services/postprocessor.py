# app/services/postprocessor.py
from typing import Dict
import logging
from interfaces.postprocessor import PostProcessor
from app.services.field_correctors.banorte_credito_cleaner import BanorteCreditoFieldCorrector
from services.ai_refiners.factory import get_ai_refiner


class StructuredPostProcessor(PostProcessor):
    def __init__(self, refiner_type: str | None):
        self.corrector = BanorteCreditoFieldCorrector()
        self.refiner = get_ai_refiner(refiner_type) if refiner_type else None

    def process(self, fields: Dict[str, str]) -> Dict:
        """Limpia y opcionalmente refina los campos extraídos del OCR."""
        structured = self.corrector.transform(fields)

        if not self.refiner:
            return structured

        for section, content in structured.items():
            try:
                if isinstance(content, dict):
                    refined_result = self.refiner.refine({section: content})
                    if isinstance(refined_result, dict) and refined_result:
                        structured[section] = next(iter(refined_result.values()))
                    else:
                        structured[section] = content
                elif isinstance(content, str):
                    refined_result = self.refiner.refine({section: content})
                    if isinstance(refined_result, dict) and section in refined_result:
                        structured[section] = refined_result[section]
                    else:
                        structured[section] = content
            except Exception as e:
                logging.warning(f"[PostProcessor] Error al refinar sección '{section}': {e}")
                structured[section] = content

        return structured
