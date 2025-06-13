# app/services/ocr/form_identifier.py

from typing import List, Dict, Optional

class FormIdentifier:
    FORM_KEYWORDS = {
        "banorte_credito": ["SOLICITUD CRÉDITO PERSONAL BANORTE"],
        "tarjeta_credito": ["SOLICITUD DE TARJETA DE CREDITO"],
        "hipotecario": ["SOLICITUD DE CREDITO HIPOTECARIO"]
    }

    @staticmethod
    def identify_form(blocks: List[Dict]) -> Optional[str]:
        for block in blocks:
            if block.get("BlockType") == "LINE" and "Text" in block:
                text = block["Text"].strip().upper()
                for form_type, keywords in FormIdentifier.FORM_KEYWORDS.items():
                    for keyword in keywords:
                        if keyword in text:
                            return form_type
        return None
