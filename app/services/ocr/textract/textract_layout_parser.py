from typing import Dict, List
from services.utils.normalization import normalize_key

class TextractLayoutParser:
    """Parse Textract LINE blocks to group data by sections."""

    def __init__(self, blocks: List[Dict]):
        self.blocks = blocks or []

    def _iter_lines(self):
        lines = [b for b in self.blocks if b.get("BlockType") == "LINE"]
        return sorted(lines, key=lambda b: (
            b.get("Page", 1),
            b.get("Geometry", {}).get("BoundingBox", {}).get("Top", 0),
            b.get("Geometry", {}).get("BoundingBox", {}).get("Left", 0),
        ))

    def _is_header(self, text: str) -> bool:
        return text.strip().upper() == "REFERENCIAS PERSONALES"

    def _is_stop(self, text: str) -> bool:
        return text.strip().upper() in {"CLAUSULAS", "CONSENTIMIENTO"}

    def parse(self) -> Dict[str, List[str]]:
        sections: Dict[str, List[str]] = {}
        current = None
        for line in self._iter_lines():
            text = line.get("Text", "").strip()
            if not text:
                continue
            if self._is_header(text):
                current = normalize_key(text)
                sections.setdefault(current, [])
                continue
            if self._is_stop(text):
                current = None
                continue
            if current and line.get("TextType") == "HANDWRITING":
                sections[current].append(text)
        return sections
