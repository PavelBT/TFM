from services.field_correctors.generic_cleaner import GenericFieldCleaner

class GenericPostProcessor:
    def __init__(self):
        self.cleaner = GenericFieldCleaner()

    def process(self, raw_fields: dict) -> dict:
        """Aplica limpieza genérica a los campos extraídos."""
        return self.cleaner.transform(raw_fields)
