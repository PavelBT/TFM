class FormIdentifier:
    """Simple form detection based on keyword presence."""

    RULES = {
        "credit_application": ["curp", "rfc", "sueldo"],
    }

    @classmethod
    def identify(cls, fields: dict) -> str:
        field_text = " ".join(k.lower() for k in fields.keys())
        for form, keywords in cls.RULES.items():
            if any(k in field_text for k in keywords):
                return form
        return "unknown"
