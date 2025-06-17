from typing import Dict
import re
from services.field_correctors.basic_field_corrector import BasicFieldCorrector
from services.utils.logger import get_logger

class GenericFieldCleaner:
    """Clean a flat dict of fields without altering keys."""

    def __init__(self):
        self.corrector = BasicFieldCorrector()
        self.logger = get_logger(self.__class__.__name__)

    @staticmethod
    def _pre_clean(value: str) -> str:
        value = re.sub(r"\s+", " ", value).strip()
        return value

    @staticmethod
    def _fix_ocr_errors(value: str) -> str:
        if any(c.isdigit() for c in value):
            value = re.sub(r"(?<=\d)[Oo](?=\d)|[Oo](?=\d)|(?<=\d)[Oo]", "0", value)
            value = re.sub(r"(?<=\d)[Il](?=\d)|[Il](?=\d)|(?<=\d)[Il]", "1", value)
        return value

    def clean(self, fields: Dict[str, str]) -> Dict[str, str]:
        cleaned: Dict[str, str] = {}
        for key, value in fields.items():
            self.logger.info("Cleaning %s: %s", key, value)
            val = self._pre_clean(str(value))
            val = self._fix_ocr_errors(val)
            corrected = self.corrector.correct(key, val)
            cleaned[key] = corrected if corrected is not None else val
            self.logger.info("Result %s: %s", key, cleaned[key])
        return cleaned
