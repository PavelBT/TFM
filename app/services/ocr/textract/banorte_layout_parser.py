from typing import Dict, List
from services.utils.normalization import normalize_key
from services.ocr.textract.textract_layout_parser import TextractLayoutParser


class BanorteLayoutParser(TextractLayoutParser):
    """Layout parser specialized for Banorte personal credit forms."""

    STOP_HEADERS = {"CLAUSULAS", "CONSENTIMIENTO"}

    def __init__(self, blocks: List[Dict]):
        super().__init__(blocks, headers=[])
        self.recognized_sections: List[str] = []

    def _is_stop(self, text: str) -> bool:
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

            upper = text.upper()
            if upper == "REFERENCIAS PERSONALES":
                current_section = normalize_key(text)
                sections.setdefault(current_section, [])
                self.recognized_sections.append(current_section)
                continue
            if self._is_stop(text):
                current_section = None
                continue
            if "INFORMACION" in upper or "INFORMACIÓN" in upper or "DOMICILIO" in upper or "EMPLEO" in upper:
                current_section = normalize_key(text)
                sections.setdefault(current_section, [])
                self.recognized_sections.append(current_section)
                continue

            if current_section:
                sections.setdefault(current_section, []).append(text)

        self.recognized_sections = list(sections.keys())
        return {k: v for k, v in sections.items() if v}
