from services.field_correctors.structured_cleaner import StructuredFieldCorrector

class StructuredOutputPostProcessor:
    """Applies StructuredFieldCorrector directly to raw OCR fields."""

    def __init__(self):
        self.cleaner = StructuredFieldCorrector()

    def process(self, raw_fields: dict, layout: dict | None = None) -> dict:
        return self.cleaner.transform(raw_fields)
