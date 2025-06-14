# app/services/field_correctors/basic_cleaner.py

import re
from typing import Optional
from app.interfaces.field_corrector import FieldCorrector

class BasicFieldCorrector(FieldCorrector):
    def correct(self, key: str, value: str) -> Optional[str]:
        # Quitar espacios sobrantes
        value = value.strip()

        # Eliminar si está vacío
        if not value:
            return None

        # Correcciones específicas
        key_lower = key.lower()

        if "correo" in key_lower or "email" in key_lower:
            # Forzar a minúscula y eliminar errores comunes
            value = value.lower().replace(" ", "").replace(",", ".")
            if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
                return None

        elif "nombre" in key_lower or "apellido" in key_lower:
            # Capitalizar
            value = value.title()

        elif "teléfono" in key_lower or "celular" in key_lower:
            value = re.sub(r"[^\d]", "", value)  # quitar todo menos números
            if len(value) < 10:  # muy corto para un número válido
                return None

        elif "monto" in key_lower:
            value = re.sub(r"[^\d]", "", value)  # quitar símbolos como "$", ","
            if not value.isdigit():
                return None

        elif "r.f.c" in key_lower or "curp" in key_lower:
            value = value.upper().replace(" ", "")

        # Otros valores opcionales pueden validarse según se requiera

        return value
