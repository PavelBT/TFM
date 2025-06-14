import unicodedata
import re

def normalize_key(key: str) -> str:
    """Normalize a field name to a consistent snake_case format."""
    key = unicodedata.normalize('NFKD', key).encode('ascii', 'ignore').decode('ascii')
    key = key.lower()
    key = re.sub(r'\(.*?\)', '', key)
    key = re.sub(r'[^a-z0-9 _]', '', key)
    key = re.sub(r'\s+', '_', key)
    return key.strip('_')
