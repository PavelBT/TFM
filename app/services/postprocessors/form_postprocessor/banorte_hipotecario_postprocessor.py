from typing import Dict
from interfaces.postprocessor import PostProcessor
from services.field_correctors.hipotecario_cleaner import HipotecarioFieldCorrector


class BanorteHipotecarioPostProcessor(PostProcessor):
    """Structured post-processing for crédito hipotecario."""

    def __init__(self) -> None:
        self.corrector = HipotecarioFieldCorrector()

    def process(self, fields: Dict[str, str]) -> Dict:
        return self.corrector.transform(fields)

