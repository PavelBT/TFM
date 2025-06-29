from typing import Dict, Any

from interfaces.postprocessor import PostProcessor
from services.field_correctors.banorte_credito_cleaner import (
    BanorteCreditoFieldCorrector,
)
from services.utils.normalization import normalize_key


_CANONICAL_MAP = {
    "nombres_sin_abreviaturas": "nombre",
    "rfc_con_homoclave": "rfc",
    "sueldo_mensual": "ingresos_mensuales",
    "ingreso_mensual": "ingresos_mensuales",
    "monto_solicitado": "monto_solicitado",
    "correo": "email",
    "correo_electronico": "email",
    "telefono_de_casa": "telefono_casa",
}

class BanorteCreditoPostProcessor(PostProcessor):
    """Apply structured cleaning and optional AI refinement."""

    def __init__(self) -> None:
        self.corrector = BanorteCreditoFieldCorrector()

    def _normalize_keys(self, data: Dict[str, Any]) -> Dict[str, Any]:
        normalized: Dict[str, Any] = {}
        for key, value in data.items():
            if isinstance(value, dict):
                value = self._normalize_keys(value)
            norm_key = normalize_key(key)
            canonical = _CANONICAL_MAP.get(norm_key, norm_key)
            normalized[canonical] = value
        return normalized

    def process(self, fields: Dict[str, str]) -> Dict:
        structured = self.corrector.transform(fields)
        return self._normalize_keys(structured)
