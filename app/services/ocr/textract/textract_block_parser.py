from typing import Dict, List

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
        self.logger.info("Extracted %s fields", len(field_dict))
        return field_dict
