from typing import Dict, List, Tuple
import re
from services.utils.logger import get_logger


class TextractBlockParser:
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    @staticmethod
    def _get_text(block: dict, block_map: dict) -> str:
        text = ""
        for rel in block.get("Relationships", []):
            if rel["Type"] == "CHILD":
                for child_id in rel["Ids"]:
                    word = block_map[child_id]
                    if word["BlockType"] in {"WORD", "CELL"}:
                        text += word.get("Text", "") + " "
                    elif (
                        word["BlockType"] == "SELECTION_ELEMENT"
                        and word.get("SelectionStatus") == "SELECTED"
                    ):
                        text += "[X] "
        return text.strip()

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
                # Prefer later non-empty values if existing value is empty or shorter
                if key_text in field_dict:
                    current = field_dict[key_text]
                    if (
                        value_text
                        and (not current or len(value_text) > len(current))
                    ):
                        field_dict[key_text] = value_text
                else:
                    field_dict[key_text] = value_text

        self.logger.info("Key-value pairs extracted: %s", len(field_dict))

        added = 0
        for block in blocks:
            if block.get("BlockType") == "LINE":
                text = block.get("Text", "").strip()
                kv = self._extract_from_line(text)
                if kv:
                    k, v = kv
                    if k not in field_dict or not field_dict[k]:
                        field_dict[k] = v
                        added += 1

        line_blocks = [b for b in blocks if b.get("BlockType") == "LINE"]
        added += self._extract_adjacent_pairs(line_blocks, field_dict)

        self.logger.info("Additional pairs from lines: %s", added)
        return field_dict
