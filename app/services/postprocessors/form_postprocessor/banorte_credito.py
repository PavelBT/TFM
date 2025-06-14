# services/postprocessors/banorte_credito.py

from services.field_correctors.form_cleaners.banorte_credito import BanorteCreditoFormProcessor
from services.field_correctors.generic_cleaner import GenericFieldCleaner



class BanorteCreditoPostProcessor:
    def __init__(self):
        self.cleaner = GenericFieldCleaner()
        self.form_processor = BanorteCreditoFormProcessor()

    def process(self, raw_fields: dict) -> dict:
        # 1. Limpieza genérica sin estructurar
        cleaned = self.cleaner.transform(raw_fields)
        structured = self.form_processor.transform(cleaned)
        return structured
