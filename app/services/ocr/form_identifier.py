from typing import List, Dict
import unicodedata


class FormIdentifier:
    """Identify a form based on OCR output."""

    # Map internal form types to the keywords that should be present in the
    # textual form name returned by the OCR service.
    RULES = {
        "credito_personal": ["banorte", "credito", "personal"],
        "credito_hipotecario": ["credito", "hipotecario"],
        "credito_tarjeta": ["basica"],
    }

    DEFAULT_TYPE = "unknown"

    @classmethod
    def identify(cls, form_name: str = "", fields: Dict | None = None) -> str:
        """Return a canonical form type from a raw form name or fields."""

        if form_name:
            normalized = ''.join(
                c for c in unicodedata.normalize('NFKD', form_name.lower())
                if not unicodedata.combining(c)
            )
        else:
            normalized = ""
        name = normalized
   
        for form, keywords in cls.RULES.items():
            if all(k in name for k in keywords):
                return form

        # Fallback: try to infer from the field names if no form name provided.
        if fields:
            field_text = " ".join(k.lower() for k in fields.keys())
            for form, keywords in cls.RULES.items():
                if all(k in field_text for k in keywords):
                    return form

        return cls.DEFAULT_TYPE

    @classmethod
    def identify_from_blocks(cls, blocks: List[Dict]) -> str:
        """Identify form type directly from Textract blocks."""
        raw_name = cls.extract_name_from_blocks(blocks)
        return cls.identify(raw_name)

    @staticmethod
    def extract_name_from_blocks(blocks: List[Dict]) -> str:
        """Return the first line of the first page as the form name."""
        for block in blocks:
            if block.get("BlockType") == "LINE" and block.get("Page", 1) == 1:
                return block.get("Text", "").strip()
        return ""
