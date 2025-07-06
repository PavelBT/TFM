import re
import unicodedata
from typing import Optional
from datetime import datetime, date

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


def parse_money(amount: str) -> Optional[str]:
    """Return a monetary value as a string with two decimals.

    Supports inputs with mixed comma and period usage such as ``1.000.00`` or
    ``1,000,00`` that may result from OCR errors. If the last punctuation
    character is followed by one or two digits it is treated as the decimal
    separator. All preceding punctuation characters are considered thousand
    separators and removed. Returns ``None`` when the value cannot be parsed.
    """

    if not amount:
        return None

    amt = amount.strip().replace("$", "").replace(" ", "")

    # Identify the last comma or period in the string
    m = re.search(r"[.,](?=[^.,]*$)", amt)
    if m:
        dec_index = m.start()
        decimals = amt[dec_index + 1:]
        if decimals.isdigit() and 0 < len(decimals) <= 2:
            integer = re.sub(r"[.,]", "", amt[:dec_index])
            amt = f"{integer}.{decimals}"
        else:
            amt = re.sub(r"[.,]", "", amt)
    else:
        amt = re.sub(r"[.,]", "", amt)

    try:
        return f"{float(amt):.2f}"
    except ValueError:
        return None


def parse_date(value: str) -> Optional[date]:
    """Parse common date formats and return a ``date`` object.

    Accepts ``dd/mm/aaaa``, ``dd-mm-aaaa`` and ``yyyy-mm-dd``. Returns ``None``
    when the value cannot be parsed or is empty.
    """

    if not value:
        return None

    value = value.strip()
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None
