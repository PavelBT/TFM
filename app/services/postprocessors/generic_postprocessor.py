from services.field_correctors.generic_cleaner import GenericFieldCleaner

class GenericPostProcessor:
    def __init__(self):
        self.cleaner = GenericFieldCleaner()

    def process(self, raw_fields: dict) -> dict:
        """Aplica limpieza genérica a los campos extraídos."""
        cleaned = self.cleaner.transform(raw_fields)
        checklist = [k for k, v in cleaned.items() if isinstance(v, str) and v.lower() == "sí"]
        for key in checklist:
            cleaned.pop(key, None)
        if checklist:
            cleaned["checklist"] = checklist
        return cleaned
