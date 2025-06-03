from typing import Dict, List


class TextractKeyValueExtractor:
    def __init__(self, blocks: List[Dict]):
        self.blocks = blocks
        self.block_map = {block["Id"]: block for block in blocks if "Id" in block}
        self.key_map = {}
        self.value_map = {}
        self.field_dict = {}

        for block in blocks:
            if block["BlockType"] == "KEY_VALUE_SET":
                if "KEY" in block.get("EntityTypes", []):
                    self.key_map[block["Id"]] = block
                elif "VALUE" in block.get("EntityTypes", []):
                    self.value_map[block["Id"]] = block

    def extract(self) -> Dict[str, str]:
        used_value_ids = set()

        for key_block_id, key_block in self.key_map.items():
            key_text = self._get_text(key_block)

            if not key_text.strip():
                continue  # clave vacía, se omite

            values = []
            for rel in key_block.get("Relationships", []):
                if rel["Type"] == "VALUE":
                    for value_id in rel["Ids"]:
                        value_block = self.value_map.get(value_id)
                        if value_block:
                            value_text = self._get_text(value_block)
                            values.append(value_text)
                            used_value_ids.add(value_id)

            self.field_dict[key_text] = " | ".join(values)

        # Paso adicional: extraer líneas sueltas que tengan estructura "clave: valor"
        for block in self.blocks:
            if block["BlockType"] == "LINE" and "Text" in block:
                text = block["Text"]
                if ":" in text:
                    key, value = map(str.strip, text.split(":", 1))
                    if key not in self.field_dict:
                        self.field_dict[key] = value

        return self.field_dict

    def _get_text(self, block: Dict) -> str:
        text = ""
        for rel in block.get("Relationships", []):
            if rel["Type"] == "CHILD":
                for child_id in rel["Ids"]:
                    child = self.block_map.get(child_id)
                    if child is None:
                        continue
                    if child["BlockType"] == "WORD":
                        text += child["Text"] + " "
                    elif child["BlockType"] == "SELECTION_ELEMENT":
                        if child["SelectionStatus"] == "SELECTED":
                            text += "[X] "
        return text.strip()