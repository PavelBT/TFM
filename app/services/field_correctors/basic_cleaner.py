# services/field_correctors/basic_cleaner.py

import re
from typing import Optional
from interfaces.field_corrector import FieldCorrector
from services.utils.normalization import normalize_key

class BasicFieldCorrector(FieldCorrector):
    def __init__(self):
        self.corrected_count = 0
        self.discarded_count = 0

    def correct(self, key: str, value: str) -> Optional[str]:
        value = value.strip()
        if value.upper() == "VALUE_NOT_FOUND":
            self.discarded_count += 1
            return None
        if not value or value.lower() in ["$", "0", "00", "000", "n/a", "na", "none", "--"]:
            self.discarded_count += 1
            return None

        key_norm = normalize_key(key)

        # Corrección de emails
        if "correo" in key_norm or "email" in key_norm:
            value = value.lower().replace(" ", "").replace(",", ".")
            if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,4}$", value):
                self.discarded_count += 1
                return None

        # Teléfonos
        elif "telefono" in key_norm or "celular" in key_norm or "oficina" in key_norm:
            value = re.sub(r"[^\d]", "", value)
            if not re.fullmatch(r"\d{10}", value):
                self.discarded_count += 1
                return None

        # Códigos postales
        elif "codigo_postal" in key_norm or "c.p" in key_norm:
            value = re.sub(r"[^\d]", "", value)
            if not re.fullmatch(r"\d{5}", value):
                self.discarded_count += 1
                return None

        # RFC
        elif "rfc" in key_norm:
            value = value.upper().replace(" ", "")
            if not re.fullmatch(r"[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}", value):
                self.discarded_count += 1
                return None

        # CURP
        elif "curp" in key_norm:
            value = value.upper().replace(" ", "")
            if not re.fullmatch(r"[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]{2}", value):
                self.discarded_count += 1
                return None

        # Montos o ingresos
        elif "monto" in key_norm or "sueldo" in key_norm or "ingreso" in key_norm:
            value = re.sub(r"[^\d]", "", value)
            if not value:
                self.discarded_count += 1
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
            self.corrected_count += 1
            return "Sí"

        value = value.strip().replace(" .", ".").replace("..", ".")
        if not value:
            self.discarded_count += 1
            return None
        if value != value.strip():
            self.corrected_count += 1
        return value

    def get_metrics(self) -> dict:
        return {
            "corrected": self.corrected_count,
            "discarded": self.discarded_count,
        }


    def _clean_name(self, value: str) -> str:
        value = value.title()
        value = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s\.\-]', '', value)
        value = re.sub(r'\s+', ' ', value)
        value = re.sub(r'[\.]+$', '', value)
        return value.strip()
