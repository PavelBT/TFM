# app/services/field_correctors/basic_cleaner.py

import re
import unicodedata
from typing import Optional
from interfaces.field_corrector import FieldCorrector

class BasicFieldCorrector(FieldCorrector):
    def correct(self, key: str, value: str) -> Optional[str]:
        value = value.strip()
        if not value or value in ["$", "0", "00", "000", "n/a", "na", "none"]:
            return None

        key_norm = self._normalize_key(key)

        # Corrección de emails
        if "correo" in key_norm or "email" in key_norm:
            value = value.lower().replace(" ", "").replace(",", ".")
            if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
                return None

        # Nombres y apellidos
        elif "nombre" in key_norm or "apellido" in key_norm:
            value = self._clean_name(value)

        # Teléfonos
        elif "telefono" in key_norm or "celular" in key_norm or "oficina" in key_norm:
            value = re.sub(r"[^\d]", "", value)
            if len(value) < 10:
                return None

        # Montos
        elif "monto" in key_norm or "sueldo" in key_norm:
            value = re.sub(r"[^\d]", "", value)
            if not value:
                return None

        # RFC y CURP
        elif "rfc" in key_norm or "curp" in key_norm:
            value = value.upper().replace(" ", "")

        # Checkbox: [X] o vacío
        elif value == "[X]":
            return "Sí"
        elif value == "":
            return None

        # Capitalizar direcciones y ocupaciones
        elif "domicilio" in key_norm or "direccion" in key_norm or "ocupacion" in key_norm:
            value = value.title()

        # Nacionalidad y país
        elif "nacionalidad" in key_norm or "pais" in key_norm:
            value = value.title()
        
              
        elif "monto" in key_norm or "sueldo" in key_norm:
            value = value.replace("$", "").replace(",", "").replace(".", "")
            value = re.sub(r"[^\d]", "", value)
            if not value:
                return None

        # Eliminar puntos y espacios extra
        value = value.strip().replace(" .", ".").replace("..", ".")
        return value if value else None

    def _normalize_key(self, key: str) -> str:
        key = unicodedata.normalize('NFKD', key).encode('ascii', 'ignore').decode('ascii')
        key = key.lower()
        key = re.sub(r'[^a-z0-9 ]', '', key)
        key = key.strip()
        return key

    def _clean_name(self, value: str) -> str:
        # Capitaliza cada palabra y elimina caracteres extraños
        value = value.title()
        value = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s\.\-]', '', value)
        value = re.sub(r'\s+', ' ', value)
        value = re.sub(r'[\.]+$', '', value)  # Elimina puntos al final
        return value.strip()