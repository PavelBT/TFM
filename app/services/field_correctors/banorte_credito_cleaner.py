# app/services/field_correctors/structured_cleaner.py

import re
from typing import Optional, Dict
from interfaces.field_corrector import FieldCorrector
from services.field_correctors.basic_field_corrector import BasicFieldCorrector


class BanorteCreditoFieldCorrector(FieldCorrector):
    def __init__(self):
        self.basic = BasicFieldCorrector()

    def _clean_key(self, key: str) -> str:
        return re.sub(r"[:\-\.]", "", key).strip().lower()

    def _is_selected(self, value: str) -> bool:
        return "[x]" in value.lower()

    def correct(self, key: str, value: str) -> Optional[str]:
        return self.basic.correct(key, value)

    def _init_structured(self) -> Dict:
        return {
            "datos_personales": {},
            "contacto": {},
            "empleo": {},
            "finanzas": {},
            "plazo_credito": None,
            "genero": None,
            "estado_civil": None,
            "regimen_matrimonial": None,
            "tipo_propiedad": None,
            "otros_ingresos": None,
            "tipo_ingreso": None,
        }

    def _finalize(self, structured: Dict, plazos: set, genero: Optional[str]) -> Dict:
        if plazos:
            structured["plazo_credito"] = max(plazos, key=int)
        else:
            structured["plazo_credito"] = ""

        structured["genero"] = genero or ""

        for key in ["regimen_matrimonial", "otros_ingresos", "tipo_ingreso", "estado_civil", "tipo_propiedad"]:
            if structured[key] is None:
                structured[key] = ""

        for k, v in structured["finanzas"].items():
            structured["finanzas"][k] = str(v) if v is not None else ""

        return structured

    def transform(self, raw_data: Dict[str, str]) -> Dict:
        structured = self._init_structured()
        plazos_detectados: set[str] = set()
        genero_detectado: Optional[str] = None

        for key, value in raw_data.items():
            clean_key = self._clean_key(key)
            corrected_value = self.correct(key, value)
            if not clean_key or not corrected_value:
                continue

            if clean_key in {"12", "18", "24", "36"} and self._is_selected(corrected_value):
                plazos_detectados.add(clean_key)
            elif "femenino" in clean_key and self._is_selected(corrected_value):
                genero_detectado = "Femenino"
            elif "masculino" in clean_key and self._is_selected(corrected_value):
                genero_detectado = "Masculino"
            elif any(et in clean_key for et in ["soltero", "casado", "unión libre", "divorciado", "viudo"]):
                if self._is_selected(corrected_value):
                    structured["estado_civil"] = key.strip().split()[0]
            elif "sociedad conyugal" in clean_key and self._is_selected(corrected_value):
                structured["regimen_matrimonial"] = "Sociedad Conyugal"
            elif "separación de bienes" in clean_key and self._is_selected(corrected_value):
                structured["regimen_matrimonial"] = "Separación de Bienes"
            elif "propia" in clean_key and self._is_selected(corrected_value):
                structured["tipo_propiedad"] = "Propia"
            elif "rentada" in clean_key and self._is_selected(corrected_value):
                structured["tipo_propiedad"] = "Rentada"
            elif "hipotecada" in clean_key and self._is_selected(corrected_value):
                structured["tipo_propiedad"] = "Hipotecada"
            elif "de familiares" in clean_key and self._is_selected(corrected_value):
                structured["tipo_propiedad"] = "De familiares"
            elif "otros ingresos" in clean_key:
                if "no" in clean_key and self._is_selected(corrected_value):
                    structured["otros_ingresos"] = "No"
                elif "sí" in clean_key and self._is_selected(corrected_value):
                    structured["otros_ingresos"] = "Sí"
            elif "asalariado" in clean_key and self._is_selected(corrected_value):
                structured["tipo_ingreso"] = "Asalariado"
            elif "honorarios" in clean_key and self._is_selected(corrected_value):
                structured["tipo_ingreso"] = "Honorarios"
            elif "sueldo mensual" in clean_key:
                sueldo = re.sub(r"[^\d]", "", corrected_value)
                structured["finanzas"]["sueldo_mensual"] = int(sueldo) if sueldo.isdigit() else None
            elif any(x in clean_key for x in ["nombre", "apellido", "curp", "rfc"]):
                structured["datos_personales"][clean_key] = corrected_value
            elif any(x in clean_key for x in ["teléfono", "celular", "correo", "email"]):
                structured["contacto"][clean_key] = corrected_value
            elif any(x in clean_key for x in ["empresa", "puesto"]):
                structured["empleo"][clean_key] = corrected_value
            elif any(x in clean_key for x in ["monto", "nómina"]):
                structured["finanzas"][clean_key] = corrected_value
            else:
                structured["datos_personales"][clean_key] = corrected_value

        return self._finalize(structured, plazos_detectados, genero_detectado)
