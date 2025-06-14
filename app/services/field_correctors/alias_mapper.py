# services/field_correctors/alias_mapper.py

import yaml
from typing import Dict, List

class AliasMapper:
    def __init__(self, alias_file: str):
        with open(alias_file, encoding="utf-8") as f:
            self.aliases = yaml.safe_load(f)

    def get(self, fields: Dict[str, str], key: str, default="") -> str:
        for alias in self.aliases.get(key, []):
            if alias in fields:
                return fields[alias].strip()
        return default

    def get_checked(self, fields: Dict[str, str], options: List[str]) -> str:
        for option in options:
            value = self.get(fields, option).lower()
            if value in {"[x]", "x", "si", "sí"}:
                return option
        return ""
