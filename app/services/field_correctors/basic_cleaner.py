# app/services/field_correctors/basic_cleaner.py

import re
from typing import Optional
from interfaces.field_corrector import FieldCorrector


class BasicFieldCorrector(FieldCorrector):
    def correct(self, key: str, value: str) -> Optional[str]:
        value = value.strip()
        if not value:
            return None

        key_lower = key.lower()

        if "correo" in key_lower or "email" in key_lower:
            value = value.lower().replace(" ", "").replace(",", ".")
            if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
                return None
        elif "nombre" in key_lower or "apellido" in key_lower:
            value = re.sub(r"[^\w\sñÑáéíóúÁÉÍÓÚ]", "", value)
            value = " ".join(part.capitalize() for part in value.split())
        elif "teléfono" in key_lower or "celular" in key_lower:
            value = re.sub(r"[^\d]", "", value)
            if len(value) < 10:
                return None
        elif "monto" in key_lower:
            value = re.sub(r"[^\d]", "", value)
            if not value.isdigit():
                return None
        elif "r.f.c" in key_lower or "rfc" in key_lower or "curp" in key_lower:
            value = re.sub(r"[\s.-]", "", value).upper()
        elif "c.p" in key_lower or "c\u00f3digo postal" in key_lower or "codigo postal" in key_lower:
            value = re.sub(r"[^\d]", "", value)
            if len(value) != 5:
                return None

        return value
