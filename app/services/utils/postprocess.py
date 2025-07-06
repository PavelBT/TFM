import re
from typing import Any


def _simplify(data: Any) -> Any:
    """Convert lists of {label/name, value} pairs to dictionaries."""
    if isinstance(data, list):
        if all(isinstance(item, dict) and 'value' in item and ('label' in item or 'name' in item)
               for item in data):
            return { (item.get('label') or item.get('name')): _simplify(item.get('value')) for item in data }
        return [_simplify(item) for item in data]
    if isinstance(data, dict):
        simplified = {k: _simplify(v) for k, v in data.items()}
        if len(simplified) == 1:
            return next(iter(simplified.values()))
        return simplified
    return data


def _clean_value(val: Any) -> Any:
    if isinstance(val, str):
        cleaned = val.strip()
        if '@' in cleaned:
            cleaned = cleaned.lower()
        digits = re.sub(r'\D', '', cleaned)
        if digits and len(digits) >= 7 and len(digits) >= len(cleaned.replace(' ', '').replace('-', '')):
            cleaned = digits
        return cleaned
    return val


def _apply_cleaning(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: _apply_cleaning(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_apply_cleaning(v) for v in data]
    return _clean_value(data)


def postprocess_fields(fields: dict) -> dict:
    """Simplify and clean OCR result fields."""
    simplified = _simplify(fields)
    return _apply_cleaning(simplified)
