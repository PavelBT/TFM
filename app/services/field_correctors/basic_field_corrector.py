# app/services/field_correctors/basic_field_corrector.py

import re
from typing import Optional
from interfaces.field_corrector import FieldCorrector


class BasicFieldCorrector(FieldCorrector):
    """Perform simple, field-level corrections."""

    @staticmethod
    def _fix_common_ocr_errors(text: str) -> str:
        """Correct common OCR mistakes like 'O' vs '0' or 'l' vs '1'."""
        if any(c.isdigit() for c in text):
            corrected = []
            for i, ch in enumerate(text):
                if ch in {"O", "o"}:
                    if (i > 0 and text[i - 1].isdigit()) or (
                        i + 1 < len(text) and text[i + 1].isdigit()
                    ):
                        corrected.append("0")
                        continue
                if ch in {"I", "l"}:
                    if (i > 0 and text[i - 1].isdigit()) or (
                        i + 1 < len(text) and text[i + 1].isdigit()
                    ):
                        corrected.append("1")
                        continue
                corrected.append(ch)
            return "".join(corrected)
        return text

    def correct(self, key: str, value: str) -> Optional[str]:
        value = re.sub(r"\s+", " ", value).strip()
        if not value:
            return None

        value = self._fix_common_ocr_errors(value)

        key_lower = key.lower()

        if "correo" in key_lower or "email" in key_lower:
            value = value.lower().replace(" ", "").replace(",", ".")
            # Keep the value even if it doesn't fully match the email pattern
            # so the raw OCR data is not discarded.
            return value if value else None
        elif "nombre" in key_lower or "apellido" in key_lower:
            value = re.sub(r"[^\w\sñÑáéíóúÁÉÍÓÚ]", "", value)
            value = " ".join(part.capitalize() for part in value.split())
        elif any(t in key_lower for t in ["teléfono", "telefono", "celular"]):
            value = re.sub(r"[^\d]", "", value)
            # Do not discard the number even if it doesn't have exactly
            # ten digits; return whatever digits were detected.
            return value if value else None
        elif "monto" in key_lower:
            from services.utils.normalization import parse_money

            value = parse_money(value)
            if value is None:
                return None
        elif "r.f.c" in key_lower or "rfc" in key_lower:
            value = re.sub(r"[\s.-]", "", value).upper()
            # Preserve the value even if it doesn't match the expected format.
            return value if value else None
        elif "curp" in key_lower:
            value = re.sub(r"[\s-]", "", value).upper()
            # Preserve even invalid CURP strings after cleaning.
            return value if value else None
        elif "c.p" in key_lower or "c\u00f3digo postal" in key_lower or "codigo postal" in key_lower:
            value = re.sub(r"[^\d]", "", value)
            # Accept postal codes even if they don't have exactly five digits.
            return value if value else None

        return value
