import re
import unicodedata

def normalize_key(key: str) -> str:
    """Normalize dictionary keys to snake_case."""
    key = key.strip().lower()
    # Normalize accented characters like "ó" -> "o" and "ñ" -> "n"
    key = "".join(
        c for c in unicodedata.normalize("NFKD", key) if not unicodedata.combining(c)
    )
    # Preserve slashes but collapse surrounding whitespace
    key = re.sub(r"\s*/\s*", "/", key)
    # Replace spaces and hyphens with underscores
    key = re.sub(r"[\s\-]+", "_", key)
    # Remove remaining unwanted characters except underscores and slashes
    key = re.sub(r"[^a-z0-9/_]", "", key)
    key = re.sub(r"_+", "_", key)
    return key.strip("_")
