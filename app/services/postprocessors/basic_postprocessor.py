from services.field_correctors.basic_cleaner import BasicFieldCorrector
from services.utils.normalization import normalize_key

class BasicPostProcessor:
    """Apply BasicFieldCorrector to raw OCR fields."""

    def __init__(self):
        self.cleaner = BasicFieldCorrector()

    def _flatten_value(self, value):
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            return " ".join(str(v) for v in value.values())
        if isinstance(value, list):
            return " ".join(self._flatten_value(v) for v in value)
        return str(value)

    def process(self, raw_fields: dict, layout: dict | None = None) -> dict:
        cleaned = {}
        for key, value in raw_fields.items():
            key_norm = normalize_key(key)
            value_flat = self._flatten_value(value)
            corrected = self.cleaner.correct(key, value_flat)
            if corrected not in [None, ""]:
                cleaned[key_norm] = corrected
        return cleaned

