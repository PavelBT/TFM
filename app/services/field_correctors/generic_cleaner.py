# Ruta: services/field_correctors/generic_cleaner.py

import logging
from typing import Dict, Optional
from interfaces.field_corrector import FieldCorrector
from services.field_correctors.basic_cleaner import BasicFieldCorrector

class GenericFieldCleaner(FieldCorrector):
    """
    Aplica limpieza básica a los datos OCR sin agrupar ni reorganizar.
    Se utiliza como paso previo o como fallback para formularios no identificados.
    """

    def __init__(self):
        self.basic = BasicFieldCorrector()

    def correct(self, key: str, value: str) -> Optional[str]:
        try:
            return self.basic.correct(key, value)
        except Exception as e:
            logging.warning(f"[GenericCleaner] Error al corregir campo '{key}': {e}")
            return None

    def _flatten_value(self, value) -> str:
        """
        Convierte un valor que puede ser dict, list o str en un str plano.
        """
        if isinstance(value, str):
            return value
        elif isinstance(value, dict):
            return next(iter(value.values()), "")
        elif isinstance(value, list):
            return " ".join(str(v) for v in value)
        else:
            return str(value)

    def transform(self, raw_data: Dict[str, object]) -> Dict[str, str]:
        """
        Aplica limpieza básica clave-valor.
        """
        cleaned = {}

        for key, value in raw_data.items():
            key = key.strip()

            value_flat = self._flatten_value(value)
            cleaned_value = self.correct(key, value_flat)

            if cleaned_value is not None:
                cleaned[key] = cleaned_value

        return cleaned