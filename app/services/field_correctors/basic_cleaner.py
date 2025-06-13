# services/field_correctors/basic_cleaner.py

import re
import unicodedata
from typing import Optional
from interfaces.field_corrector import FieldCorrector

class BasicFieldCorrector(FieldCorrector):
    def correct(self, key: str, value: str) -> Optional[str]:
        value = value.strip()
        if not value or value.lower() in ["$", "0", "00", "000", "n/a", "na", "none", "--"]:
            return None

        key_norm = self._normalize_key(key)

        # Corrección de emails
        if "correo" in key_norm or "email" in key_norm:
            value = value.lower().replace(" ", "").replace(",", ".")
            if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,4}$", value):
                return None

        # Teléfonos
        elif "telefono" in key_norm or "celular" in key_norm or "oficina" in key_norm:
            value = re.sub(r"[^\d]", "", value)
            if not re.fullmatch(r"\d{10}", value):
                return None

        # Códigos postales
        elif "codigo_postal" in key_norm or "c.p" in key_norm:
            value = re.sub(r"[^\d]", "", value)
            if not re.fullmatch(r"\d{5}", value):
                return None

        # RFC
        elif "rfc" in key_norm:
            value = value.upper().replace(" ", "")
            if not re.fullmatch(r"[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}", value):
                return None

        # CURP
        elif "curp" in key_norm:
            value = value.upper().replace(" ", "")
            if not re.fullmatch(r"[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]{2}", value):
                return None

        # Montos o ingresos
        elif "monto" in key_norm or "sueldo" in key_norm or "ingreso" in key_norm:
            value = re.sub(r"[^\d]", "", value)
            if not value:
                return None

        # Nombres y apellidos
        elif "nombre" in key_norm or "apellido" in key_norm:
            value = self._clean_name(value)

        # Domicilio y ocupación
        elif "domicilio" in key_norm or "direccion" in key_norm or "ocupacion" in key_norm:
            value = value.title()

        # Nacionalidad y país
        elif "nacionalidad" in key_norm or "pais" in key_norm:
            value = value.title()

        # Checkbox
        elif value.strip().upper() in ["[X]", "X"]:
            return "Sí"

        value = value.strip().replace(" .", ".").replace("..", ".")
        return value if value else None

    def _normalize_key(self, key: str) -> str:
        key = unicodedata.normalize('NFKD', key).encode('ascii', 'ignore').decode('ascii')
        key = key.lower()
        key = re.sub(r'[^a-z0-9 ]', '', key)
        key = key.strip()
        return key

    def _clean_name(self, value: str) -> str:
        value = value.title()
        value = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s\.\-]', '', value)
        value = re.sub(r'\s+', ' ', value)
        value = re.sub(r'[\.]+$', '', value)
        return value.strip()