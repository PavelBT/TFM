from typing import Dict, List

from services.utils.normalization import normalize_key


class TextractBlockParser:
    """Parse AWS Textract blocks into a simple key/value mapping."""

    def __init__(self, blocks: List[Dict], *, normalize_keys: bool = True, use_line_fallback: bool = False):
        self.blocks = blocks or []
        self.normalize_keys = normalize_keys
        self.use_line_fallback = use_line_fallback
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
            key_text = self._get_key_text(block)
            value_ids = []
            for rel in block.get("Relationships", []):
                if rel["Type"] == "VALUE":
                    value_ids.extend(rel["Ids"])
            values = [self._get_value_text(self.block_map.get(vid, {})) for vid in value_ids]
            values = [v for v in values if v]
            if not key_text:
                continue
            key_norm = normalize_key(key_text) if self.normalize_keys else key_text
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

        if self.use_line_fallback:
            self._extract_from_lines()

        return self.field_dict

    def _get_key_text(self, block: Dict) -> str:
        return self._get_text(block)

    def _get_value_text(self, block: Dict) -> str:
        return self._get_text(block)

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

    def _extract_from_lines(self) -> None:
        lines = [b for b in self.blocks if b.get("BlockType") == "LINE"]
        for line in lines:
            text = line.get("Text", "")
            if ":" not in text:
                continue
            key, val = [t.strip() for t in text.split(":", 1)]
            if not key or not val:
                continue
            key_norm = normalize_key(key) if self.normalize_keys else key
            existing = self.field_dict.get(key_norm)
            if existing and existing != "VALUE_NOT_FOUND":
                continue
            self.field_dict[key_norm] = val
