from typing import Dict, List
import uuid
from services.utils.normalization import normalize_key


class TextractFullExtractor:
    def __init__(self, blocks: List[Dict]):
        self.blocks = blocks
        self.block_map = {block["Id"]: block for block in blocks if "Id" in block}
        self.word_map = self._build_word_map()
        self.key_map, self.value_map = self._get_key_value_maps()
        self.field_dict = {}
        self.lines = [block for block in blocks if block["BlockType"] == "LINE"]
        self.selection_elements = [block for block in blocks if block["BlockType"] == "SELECTION_ELEMENT"]

    def extract(self) -> Dict[str, str]:
        """Extrae y normaliza los campos detectados por Textract."""
        self._extract_kv_pairs()
        self._add_inline_pairs()
        self._add_colon_split_pairs()
        self._extract_consecutive_fields()
        self._extract_checkboxes()
        return self.field_dict

    def _extract_kv_pairs(self):
        kv_map = self._get_final_kv_map(self.key_map, self.value_map)
        for key, value in kv_map.items():
            key_norm = normalize_key(key)
            self.field_dict[key_norm] = value if value else "VALUE_NOT_FOUND"

    def _add_inline_pairs(self):
        for block in self.lines:
            text = block.get("Text", "")
            if ":" in text:
                key, value = map(str.strip, text.split(":", 1))
                key_norm = normalize_key(key)
                if not key:
                    continue
                if (
                    key_norm not in self.field_dict
                    or self.field_dict.get(key_norm) == "VALUE_NOT_FOUND"
                ):
                    self.field_dict[key_norm] = value

    def _add_colon_split_pairs(self):
        for idx, block in enumerate(self.lines[:-1]):
            text = block.get("Text", "").strip()
            if text.endswith(":"):
                next_text = self.lines[idx + 1].get("Text", "").strip()
                if next_text and ":" not in next_text:
                    key = text[:-1].strip()
                    if key:
                        key_norm = normalize_key(key)
                        if (
                            key_norm not in self.field_dict
                            or self.field_dict.get(key_norm) == "VALUE_NOT_FOUND"
                        ):
                            self.field_dict[key_norm] = next_text

    def _build_word_map(self) -> Dict[str, str]:
        word_map = {}
        for block in self.blocks:
            if block["BlockType"] == "WORD":
                word_map[block["Id"]] = block["Text"]
            if block["BlockType"] == "SELECTION_ELEMENT":
                word_map[block["Id"]] = block["SelectionStatus"]
        return word_map

    def _get_key_value_maps(self):
        key_map = {}
        value_map = {}
        for block in self.blocks:
            if block["BlockType"] == "KEY_VALUE_SET":
                if "KEY" in block.get("EntityTypes", []):
                    key_text = ""
                    value_ids = []
                    for rel in block.get("Relationships", []):
                        if rel["Type"] == "CHILD":
                            key_text = " ".join([self.word_map.get(i, "") for i in rel["Ids"]])
                        if rel["Type"] == "VALUE":
                            value_ids = rel["Ids"]
                    if key_text:
                        key_map[key_text] = value_ids
                elif "VALUE" in block.get("EntityTypes", []):
                    value_text = ""
                    if "Relationships" in block:
                        for rel in block["Relationships"]:
                            if rel["Type"] == "CHILD":
                                value_text = " ".join([self.word_map.get(i, "") for i in rel["Ids"]])
                    value_map[block["Id"]] = value_text if value_text else "VALUE_NOT_FOUND"
        return key_map, value_map

    def _get_final_kv_map(self, key_map, value_map):
        final_map = {}
        for key, value_ids in key_map.items():
            seen = set()
            values = []
            for k in value_ids:
                val = value_map.get(k, "VALUE_NOT_FOUND")
                if val not in seen:
                    seen.add(val)
                    values.append(val)
            final_map[key] = " | ".join(values)
        return final_map

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


    def _extract_consecutive_fields(self):
        """Attempt to infer key/value pairs from consecutive lines.

        This is a heuristic method used when a field label is on one line and
        its value appears on the following line without any delimiter.  It does
        not rely on any predefined list of field names so it can work with
        arbitrary forms.
        """

        i = 0
        while i < len(self.lines) - 1:
            key_raw = self.lines[i].get("Text", "").strip()
            value_raw = self.lines[i + 1].get("Text", "").strip()

            # Ignore obvious non-field patterns
            if not key_raw or ":" in key_raw:
                i += 1
                continue
            if not value_raw or ":" in value_raw:
                i += 1
                continue

            key = normalize_key(key_raw)

            if not key:
                i += 1
                continue

            if (
                key not in self.field_dict
                or self.field_dict.get(key) == "VALUE_NOT_FOUND"
            ):
                self.field_dict[key] = value_raw
                i += 2
            else:
                i += 1

    def _extract_checkboxes(self):
        selected_ids = {
            block["Id"]
            for block in self.selection_elements
            if block.get("SelectionStatus") == "SELECTED"
        }

        # Primero usar relaciones VALUE de Textract
        for block in self.blocks:
            if (
                block["BlockType"] == "KEY_VALUE_SET"
                and "KEY" in block.get("EntityTypes", [])
            ):
                key_text = self._get_text(block)
                value_ids = []
                for rel in block.get("Relationships", []):
                    if rel["Type"] == "VALUE":
                        value_ids.extend(rel["Ids"])
                if not key_text or not value_ids:
                    continue
                selected = False
                for val_id in value_ids:
                    val_block = self.block_map.get(val_id)
                    if not val_block:
                        continue
                    for rel in val_block.get("Relationships", []):
                        if rel["Type"] == "CHILD":
                            for child_id in rel["Ids"]:
                                if child_id in selected_ids:
                                    selected = True
                                    break
                        if selected:
                            break
                    if selected:
                        break
                if selected:
                    campo = normalize_key(key_text)
                    if (
                        campo not in self.field_dict
                        or self.field_dict.get(campo) in {"SELECTED", "NOT_SELECTED"}
                    ):
                        self.field_dict[campo] = "Sí"

        # Fallback: línea previa al checkbox
        for line in self.lines:
            rels = line.get("Relationships", [])
            for rel in rels:
                if rel["Type"] == "CHILD":
                    for child_id in rel["Ids"]:
                        if child_id in selected_ids:
                            text = line.get("Text", "")
                            idx = self.lines.index(line)
                            if idx > 0:
                                campo = normalize_key(
                                    self.lines[idx - 1].get("Text", "")
                                )
                                if campo and campo not in self.field_dict:
                                    self.field_dict[campo] = text

    # (Opcional) Método para extraer tablas si tu formulario las tiene
    def extract_tables(self):
        tables = {}
        for block in self.blocks:
            if block["BlockType"] == "TABLE":
                key = f"table_{uuid.uuid4().hex}"
                temp_table = []
                current_row = []
                last_row_index = 1
                for cell in [b for b in self.blocks if b["BlockType"] == "CELL" and b["ParentId"] == block["Id"]]:
                    row_index = cell["RowIndex"]
                    if row_index != last_row_index:
                        temp_table.append(current_row)
                        current_row = []
                        last_row_index = row_index
                    cell_text = ""
                    if "Relationships" in cell:
                        for rel in cell["Relationships"]:
                            if rel["Type"] == "CHILD":
                                cell_text = " ".join([self.word_map.get(i, "") for i in rel["Ids"]])
                    current_row.append(cell_text)
                if current_row:
                    temp_table.append(current_row)
                tables[key] = temp_table
        return tables
