from typing import Dict
from interfaces.postprocessor import PostProcessor
from services.field_correctors.structured_cleaner import StructuredFieldCorrector
from services.ai_refiners.factory import get_ai_refiner


class StructuredOutputPostProcessor(PostProcessor):
    """Apply structured cleaning and optional AI refinement."""

    def __init__(self, refiner_type: str | None):
        self.corrector = StructuredFieldCorrector()
        self.refiner = get_ai_refiner(refiner_type)

    def process(self, fields: Dict[str, str]) -> Dict:
        structured = self.corrector.transform(fields)

        if not self.refiner:
            return structured

        for section, content in structured.items():
            try:
                result = self.refiner.refine({section: content})
                if isinstance(content, dict):
                    if isinstance(result, dict) and result:
                        structured[section] = next(iter(result.values()))
                else:
                    if isinstance(result, dict) and section in result:
                        structured[section] = result[section]
            except Exception:
                # if refinement fails keep original
                structured[section] = content
        return structured
