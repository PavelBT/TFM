from typing import Dict
from interfaces.postprocessor import PostProcessor
from services.field_correctors.banorte_credito_cleaner import BanorteCreditoFieldCorrector

class BanorteCreditoPostProcessor(PostProcessor):
    """Apply structured cleaning and optional AI refinement."""

    def __init__(self) -> None:
        self.corrector = BanorteCreditoFieldCorrector()

    def process(self, fields: Dict[str, str]) -> Dict:
        structured = self.corrector.transform(fields)
        return structured
