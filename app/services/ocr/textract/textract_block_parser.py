from typing import Dict, List, Tuple
import re
from services.utils.logger import get_logger
from trp import Document


class TextractBlockParser:
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    @staticmethod
    def _default_geometry() -> dict:
        return {
            "BoundingBox": {
                "Width": 1.0,
                "Height": 1.0,
                "Left": 0.0,
                "Top": 0.0,
            },
            "Polygon": [
                {"X": 0.0, "Y": 0.0},
                {"X": 1.0, "Y": 0.0},
                {"X": 1.0, "Y": 1.0},
                {"X": 0.0, "Y": 1.0},
            ],
        }

    @classmethod
    def _prepare_blocks(cls, blocks: List[dict]) -> List[dict]:
        prepared: List[dict] = []
        has_page = any(b.get("BlockType") == "PAGE" for b in blocks)
        if not has_page:
            prepared.append(
                {
                    "Id": "page_0",
                    "BlockType": "PAGE",
                    "Geometry": cls._default_geometry(),
                    "Confidence": 1.0,
                }
            )
        for b in blocks:
            new_b = b.copy()
            new_b.setdefault("Confidence", 1.0)
            new_b.setdefault("Geometry", cls._default_geometry())
            prepared.append(new_b)
        return prepared

    def _extract_from_line(self, text: str) -> Tuple[str, str] | None:
        if ':' in text:
            key, value = text.split(':', 1)
            key, value = key.strip(), value.strip()
            if key and value:
                return key, value
        match = re.match(r"(.{3,50}?)[ \t]{2,}(.*)", text)
        if match:
            key, value = match.group(1).strip(), match.group(2).strip()
            if key and value:
                return key, value
        return None

    @staticmethod
    def _extract_adjacent_pairs(lines: List[dict], field_dict: Dict[str, str]) -> int:
        added = 0
        for i in range(len(lines) - 1):
            first = lines[i].get("Text", "").strip()
            second = lines[i + 1].get("Text", "").strip()
            if not first or not second or first in field_dict:
                continue
            if ":" in first or re.search(r"\s{2,}", first):
                continue
            if first not in field_dict and len(first.split()) <= 6:
                if second and second not in field_dict.values():
                    field_dict[first] = second
                    added += 1
        return added

    def parse(self, blocks: List[dict]) -> Dict[str, str]:
        self.logger.info("Parsing %s blocks", len(blocks))
        processed = self._prepare_blocks(blocks)
        doc = Document({"Blocks": processed})
        field_dict: Dict[str, str] = {}
        for page in doc.pages:
            for field in page.form.fields:
                key = field.key.text.strip() if field.key else ""
                value = field.value.text.strip() if field.value else ""
                if key:
                    field_dict[key] = value
        added = 0
        for block in blocks:
            if block.get("BlockType") == "LINE":
                text = block.get("Text", "").strip()
                kv = self._extract_from_line(text)
                if kv:
                    k, v = kv
                    if k not in field_dict:
                        field_dict[k] = v
                        added += 1
        line_blocks = [b for b in blocks if b.get("BlockType") == "LINE"]
        added += self._extract_adjacent_pairs(line_blocks, field_dict)
        self.logger.info("Extracted %s fields (%s from lines)", len(field_dict), added)
        return field_dict
