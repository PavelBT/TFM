from typing import Dict, Any
from interfaces.postprocessor import PostProcessor
from services.field_correctors.basic_field_corrector import BasicFieldCorrector
from services.utils.normalization import normalize_key


class BasicPostProcessor(PostProcessor):
    def __init__(self):
        self.corrector = BasicFieldCorrector()

    def process(self, fields: Dict[str, Any]) -> Dict:
        processed: Dict[str, str] = {}
        for key, value in fields.items():
            clean = self.corrector.correct(key, value)
            if clean is not None:
                processed[normalize_key(key)] = clean
        return processed
