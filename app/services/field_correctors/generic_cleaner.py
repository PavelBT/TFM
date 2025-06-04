# Ruta: services/field_correctors/generic_cleaner.py

import logging
from typing import Dict, Optional
from interfaces.field_corrector import FieldCorrector
from services.field_correctors.basic_cleaner import BasicFieldCorrector
import unicodedata
import re

class GenericFieldCleaner(FieldCorrector):
    """
    Limpieza y normalización avanzada de datos OCR.
    """

    def __init__(self):
        self.basic = BasicFieldCorrector()

    def correct(self, key: str, value: str) -> Optional[str]:
        try:
            return self.basic.correct(key, value)
        except Exception as e:
            logging.warning(f"[GenericCleaner] Error al corregir campo '{key}' (valor: '{value}'): {e}")
            return None

    def _flatten_value(self, value) -> str:
        if isinstance(value, str):
            return value
        elif isinstance(value, dict):
            return " ".join(str(v) for v in value.values())
        elif isinstance(value, list):
            return " ".join(self._flatten_value(v) for v in value)
        else:
            return str(value)

    def _normalize_key(self, key: str) -> str:
        key = unicodedata.normalize('NFKD', key).encode('ascii', 'ignore').decode('ascii')
        key = key.lower()
        key = re.sub(r'[^a-z0-9 ]', '', key)
        key = re.sub(r'\s+', '_', key)  # Espacios a guiones bajos
        return key.strip('_')

    def transform(self, raw_data: Dict[str, object]) -> Dict[str, str]:
        """
        Limpieza y normalización de todos los campos.
        """
        cleaned = {}
        for key, value in raw_data.items():
            key_norm = self._normalize_key(key)
            value_flat = self._flatten_value(value)
            cleaned_value = self.correct(key, value_flat)
            if cleaned_value not in [None, ""]:
                cleaned[key_norm] = cleaned_value
        return cleaned