from typing import Dict, List

from services.utils.normalization import normalize_key


class TextractBlockParser:
    """Parse AWS Textract blocks into a simple key/value mapping."""

    def __init__(self, blocks: List[Dict], *, normalize_keys: bool = True, use_line_fallback: bool = False):
        self.blocks = blocks or []
        self.normalize_keys = normalize_keys
        self.use_line_fallback = use_line_fallback
        self.block_map = {b["Id"]: b for b in self.blocks if "Id" in b}
        self.field_dict: Dict[str, str] = {}

    def extract(self) -> Dict[str, str]:
        self.field_dict = self._extract_fields(self.blocks)
        if self.use_line_fallback:
            self._extract_from_lines()

        return self.field_dict

    def _extract_fields(self, blocks: list) -> Dict[str, str]:
        key_map = {}
        value_map = {}
        block_map = {}

        for block in blocks:
            block_id = block["Id"]
            block_map[block_id] = block
            if block["BlockType"] == "KEY_VALUE_SET":
                if "KEY" in block.get("EntityTypes", []):
                    key_map[block_id] = block
                elif "VALUE" in block.get("EntityTypes", []):
                    value_map[block_id] = block

        field_dict: Dict[str, str] = {}
        for key_block_id, key_block in key_map.items():
            key_text = self._get_text(key_block, block_map)
            value_text = ""

            for relationship in key_block.get("Relationships", []):
                if relationship["Type"] == "VALUE":
                    for value_id in relationship["Ids"]:
                        value_block = value_map.get(value_id)
                        if value_block:
                            value_text = self._get_text(value_block, block_map)

            if key_text:
                key_norm = normalize_key(key_text) if self.normalize_keys else key_text
                field_dict[key_norm] = value_text

        return field_dict

    def _get_text(self, block: Dict, block_map: Dict) -> str:
        text = ""
        for rel in block.get("Relationships", []):
            if rel["Type"] == "CHILD":
                for child_id in rel["Ids"]:
                    word = block_map[child_id]
                    if word["BlockType"] == "WORD":
                        text += word.get("Text", "") + " "
                    elif word["BlockType"] == "SELECTION_ELEMENT" and word.get("SelectionStatus") == "SELECTED":
                        text += "[X] "
        return text.strip()

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
