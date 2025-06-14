from services.field_correctors.generic_cleaner import GenericFieldCleaner


class GenericPostProcessor:
    FIELD_ALIASES = {
        "empresa_donde_trabaja": "empresa",
        "empresa_donde_trabajo": "empresa",
    }

    def __init__(self):
        self.cleaner = GenericFieldCleaner()

    def process(self, raw_fields: dict) -> dict:
        """Aplica limpieza genérica a los campos extraídos."""
        cleaned = self.cleaner.transform(raw_fields)

        # Unify aliases before further processing
        for alias, canonical in self.FIELD_ALIASES.items():
            if alias in cleaned:
                cleaned.setdefault(canonical, cleaned[alias])
                cleaned.pop(alias)

        # Remove stray yes/no keys lacking context
        for k in ("si", "no"):
            val = cleaned.get(k)
            if val is None or val.upper() in {"", "VALUE_NOT_FOUND"}:
                cleaned.pop(k, None)
        checklist = [k for k, v in cleaned.items() if isinstance(v, str) and v.lower() == "sí"]
        for key in checklist:
            cleaned.pop(key, None)
        if checklist:
            cleaned["checklist"] = checklist
        return cleaned
