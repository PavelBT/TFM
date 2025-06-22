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
                    if word["BlockType"] == "WORD":
                        text += word["Text"] + " "
                    elif word["BlockType"] == "SELECTION_ELEMENT" and word["SelectionStatus"] == "SELECTED":
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
            if key_text and (key_text not in field_dict or not field_dict[key_text]):
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

        self.logger.info("Additional pairs from lines: %s", added)
        return field_dict
