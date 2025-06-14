from typing import Dict, List
from services.utils.normalization import normalize_key


class BanorteLayoutParser:
    """Layout parser specialized for Banorte personal credit forms."""

    STOP_HEADERS = {"CLAUSULAS", "CONSENTIMIENTO"}

    def __init__(self, blocks: List[Dict]):
        self.blocks = blocks or []

    def _iter_lines(self) -> List[Dict]:
        lines = [b for b in self.blocks if b.get("BlockType") == "LINE"]
        return sorted(
            lines,
            key=lambda b: (
                b.get("Page", 1),
                b.get("Geometry", {}).get("BoundingBox", {}).get("Top", 0),
                b.get("Geometry", {}).get("BoundingBox", {}).get("Left", 0),
            ),
        )

    def _is_stop_header(self, text: str) -> bool:
        return text.strip().upper() in self.STOP_HEADERS

    def parse(self) -> Dict[str, List[str]]:
        sections: Dict[str, List[str]] = {}
        current_section = None
        page = 1

        for line in self._iter_lines():
            text = line.get("Text", "").strip()
            if not text:
                continue

            if line.get("Page", 1) != page:
                current_section = None
                page = line.get("Page", 1)

            if line.get("TextType") != "HANDWRITING":
                upper = text.upper()
                if upper == "REFERENCIAS PERSONALES":
                    current_section = normalize_key(text)
                    sections.setdefault(current_section, [])
                elif self._is_stop_header(text):
                    current_section = None
                elif "INFORMACION" in upper or "INFORMACIÓN" in upper or "DOMICILIO" in upper or "EMPLEO" in upper:
                    current_section = normalize_key(text)
                    sections.setdefault(current_section, [])
                continue

            if current_section:
                sections.setdefault(current_section, []).append(text)

        return {k: v for k, v in sections.items() if v}
