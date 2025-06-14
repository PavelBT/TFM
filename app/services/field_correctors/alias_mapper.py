# services/field_correctors/alias_mapper.py

import yaml
from typing import Dict, List
from services.utils.normalization import normalize_key

class AliasMapper:
    def __init__(self, alias_file: str):
        with open(alias_file, encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}

        # ``yaml.safe_load`` may interpret unquoted values such as ``no`` or
        # ``yes`` as booleans. ``normalize_key`` expects strings, so convert all
        # keys and values to ``str`` before normalisation to avoid ``TypeError``.
        self.aliases = {
            normalize_key(str(k)):
            [normalize_key(str(a)) for a in (v or [])]
            for k, v in raw.items()
        }

    def _normalize_fields(self, fields: Dict[str, str]) -> Dict[str, str]:
        return {normalize_key(k): v for k, v in fields.items()}

    def get(self, fields: Dict[str, str], key: str, default="") -> str:
        fields_norm = self._normalize_fields(fields)
        key_norm = normalize_key(key)
        for alias in self.aliases.get(key_norm, []):
            if alias in fields_norm:
                return fields_norm[alias].strip()
        return default

    def get_checked(self, fields: Dict[str, str], options: List[str]) -> str:
        fields_norm = self._normalize_fields(fields)
        for option in options:
            option_norm = normalize_key(option)
            for alias in self.aliases.get(option_norm, []):
                value = fields_norm.get(alias, "").lower()
                if value in {"[x]", "x", "si", "sí"}:
                    return option
        return ""
