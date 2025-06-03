# Ruta: services/postprocessors/banorte_credito.py

from services.postprocessor import StructuredPostProcessor
from services.field_correctors.form_cleaners.banorte_credito import BanorteCreditoFormProcessor

class BanorteCreditoPostProcessor(StructuredPostProcessor):
    def process(self, fields):
        structured = super().process(fields)
        return BanorteCreditoFormProcessor().transform(structured)