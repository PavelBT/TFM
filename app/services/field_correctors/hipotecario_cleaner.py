from typing import Dict, Optional
import re
import unicodedata
from interfaces.field_corrector import FieldCorrector
from services.field_correctors.basic_field_corrector import BasicFieldCorrector


class HipotecarioFieldCorrector(FieldCorrector):
    """Clean and structure fields for crédito hipotecario forms."""

    def __init__(self) -> None:
        self.basic = BasicFieldCorrector()

    def correct(self, key: str, value: str) -> Optional[str]:
        return self.basic.correct(key, value)

    def _clean_key(self, key: str) -> str:
        key = re.sub(r"[:\-\.]+", "", key).strip().lower()
        key = "".join(c for c in unicodedata.normalize("NFKD", key) if not unicodedata.combining(c))
        return key

    def transform(self, raw_data: Dict[str, str]) -> Dict:
        structured = {
            "datos_personales": {},
            "contacto": {},
            "finanzas": {},
        }
        fecha_parts = {"dia": None, "mes": None, "ano": None}

        for key, value in raw_data.items():
            clean_key = self._clean_key(key)
            corrected = self.basic.correct(key, value)
            if not corrected:
                continue

            if clean_key in {"dia", "mes", "ano"}:
                fecha_parts[clean_key] = corrected
            elif clean_key in {"nombre", "apellido_paterno", "apellido_materno", "rfc", "curp"}:
                structured["datos_personales"][clean_key] = corrected
            elif "correo" in clean_key or "email" in clean_key:
                structured["contacto"]["email"] = corrected
            elif "celular" in clean_key:
                structured["contacto"]["telefono_celular"] = corrected
            elif "telefono" in clean_key:
                structured["contacto"]["telefono_casa"] = corrected
            elif any(x in clean_key for x in ["monto", "ingreso", "valor"]):
                structured["finanzas"][clean_key] = corrected
            else:
                structured[clean_key] = corrected

        if all(fecha_parts.values()):
            y = fecha_parts["ano"] or ""
            m = fecha_parts["mes"] or ""
            d = fecha_parts["dia"] or ""
            structured["datos_personales"]["fecha_nacimiento"] = f"{y}-{m.zfill(2)}-{d.zfill(2)}"

        return structured

