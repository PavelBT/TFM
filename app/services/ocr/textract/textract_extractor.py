from typing import Dict, List

from services.utils.normalization import normalize_key


class TextractExtractor:
    """Simple extractor for AWS Textract blocks."""

    def __init__(self, blocks: List[Dict]):
        self.blocks = blocks or []
        self.block_map = {b["Id"]: b for b in self.blocks if "Id" in b}
        self.word_map = {
            b["Id"]: b.get("Text", "")
            for b in self.blocks
            if b.get("BlockType") == "WORD"
        }
        self.selection_map = {
            b["Id"]: b.get("SelectionStatus")
            for b in self.blocks
            if b.get("BlockType") == "SELECTION_ELEMENT"
        }
        self.field_dict: Dict[str, str] = {}

    def extract(self) -> Dict[str, str]:
        for block in self.blocks:
            if block.get("BlockType") != "KEY_VALUE_SET" or "KEY" not in block.get(
                "EntityTypes", []
            ):
                continue
            key_text = self._get_text(block)
            value_ids = []
            for rel in block.get("Relationships", []):
                if rel["Type"] == "VALUE":
                    value_ids.extend(rel["Ids"])
            values = [self._get_text(self.block_map.get(vid, {})) for vid in value_ids]
            values = [v for v in values if v]
            if not key_text:
                continue
            key_norm = normalize_key(key_text)
            if values:
                dedup = []
                seen = set()
                for val in values:
                    if val not in seen:
                        seen.add(val)
                        dedup.append(val)
                self.field_dict[key_norm] = " | ".join(dedup)
            else:
                self.field_dict[key_norm] = "VALUE_NOT_FOUND"
        return self.field_dict

    def _get_text(self, block: Dict) -> str:
        parts = []
        for rel in block.get("Relationships", []):
            if rel["Type"] == "CHILD":
                for cid in rel["Ids"]:
                    if cid in self.word_map:
                        parts.append(self.word_map[cid])
                    elif cid in self.selection_map:
                        if self.selection_map[cid] == "SELECTED":
                            parts.append("Sí")
        return " ".join(parts).strip()
