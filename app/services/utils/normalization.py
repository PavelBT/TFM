import re

def normalize_key(key: str) -> str:
    """Normalize dictionary keys to snake_case."""
    key = key.strip().lower()
    key = re.sub(r"[^a-z0-9]+", "_", key)
    return key.strip("_")
