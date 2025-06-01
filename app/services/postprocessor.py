# app/services/postprocessor.py

from typing import Dict
from interfaces.postprocessor import PostProcessor
from services.field_correctors.structured_cleaner import StructuredFieldCorrector
from services.ai_refiners.huggingface_refiner import HuggingFaceRefiner


class StructuredPostProcessor(PostProcessor):
    def __init__(self):
        self.corrector = StructuredFieldCorrector()
        self.refiner = HuggingFaceRefiner()

    def process(self, fields: Dict[str, str]) -> Dict:
        """
        Limpia, transforma, organiza, mejora con IA los campos extraídos del OCR.
        """
        # Paso 1: estructura, agrupa y limpia
        structured = self.corrector.transform(fields)

        # Paso 2: refinar por secciones
        for section, content in structured.items():
            if isinstance(content, dict):
                structured[section] = self.refiner.refine(content)  # refinamos subcampos
            elif isinstance(content, str):
                structured[section] = self.refiner.refine({section: content})[section]

        return structured