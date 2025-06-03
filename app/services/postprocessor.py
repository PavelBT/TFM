from typing import Dict
from interfaces.postprocessor import PostProcessor
from services.field_correctors.generic_cleaner import GenericFieldCleaner
from services.ai_refiners.factory import get_ai_refiner
import logging

class StructuredPostProcessor(PostProcessor):
    def __init__(self, refiner_type):
        self.corrector = GenericFieldCleaner()
        self.refiner = get_ai_refiner(refiner_type)

    def process(self, fields: Dict[str, str]) -> Dict:
        """
        Limpia, transforma, organiza, mejora con IA los campos extraídos del OCR.
        """
        structured = self.corrector.transform(fields)

        for section, content in structured.items():
            try:
                if isinstance(content, dict):
                    # Refinamos el bloque completo y tomamos el primer valor
                    refined_result = self.refiner.refine({section: content})
                    if isinstance(refined_result, dict) and refined_result:
                        structured[section] = next(iter(refined_result.values()))
                    else:
                        structured[section] = content  # fallback
                elif isinstance(content, str):
                    refined_result = self.refiner.refine({section: content})
                    if isinstance(refined_result, dict) and section in refined_result:
                        structured[section] = refined_result[section]
                    else:
                        structured[section] = content  # fallback
            except Exception as e:
                logging.warning(f"[PostProcessor] Error al refinar sección '{section}': {e}")
                structured[section] = content  # fallback

        return structured