from typing import Dict, List
import uuid
from services.utils.normalization import normalize_key
from pathlib import Path

class TextractFullExtractor:
    def __init__(self, blocks: List[Dict], alias_file: str = None):
        self.blocks = blocks
        self.block_map = {block["Id"]: block for block in blocks if "Id" in block}
        self.word_map = self._build_word_map()
        self.key_map, self.value_map = self._get_key_value_maps()
        self.field_dict = {}
        self.lines = [block for block in blocks if block["BlockType"] == "LINE"]
        self.selection_elements = [block for block in blocks if block["BlockType"] == "SELECTION_ELEMENT"]
        self.alias_mapper = None
        if alias_file is None:
            alias_file = str(Path(__file__).resolve().parent / "aliases" / "consecutive_aliases.yaml")
        if alias_file:
            from services.field_correctors.alias_mapper import AliasMapper
            self.alias_mapper = AliasMapper(alias_file)

    def extract(self) -> Dict[str, str]:
        """Extrae y normaliza los campos detectados por Textract."""
        self._extract_kv_pairs()
        self._add_inline_pairs()
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
                if key and key_norm not in self.field_dict:
                    self.field_dict[key_norm] = value

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
            values = [value_map.get(k, "VALUE_NOT_FOUND") for k in value_ids]
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
        campos = [
            "nombre(s) (sin abreviaturas)", "apellido paterno", "apellido materno",
            "fecha de nacimiento", "pais de nacimiento", "nacionalidad", "genero",
            "telefono de casa", "telefono celular", "e-mail", "tipo de identificacion",
            "folio", "estado civil", "regimen matrimonial", "domicilio (calle y numero exterior e interior)",
            "colonia/urbanizacion", "delegacion/municipio/demarcacion politica", "ciudad/poblacion",
            "entidad federativa/estado", "pais", "cp", "anos de residencia"
        ]
        campos_norm = [normalize_key(c) for c in campos]
        alias_map = {}
        if self.alias_mapper:
            alias_map = {
                normalize_key(base): [normalize_key(a) for a in aliases]
                for base, aliases in self.alias_mapper.aliases.items()
            }

        i = 0
        while i < len(self.lines) - 1:
            key_raw = self.lines[i].get("Text", "")
            key = normalize_key(key_raw)
            campo = None
            if key in campos_norm:
                campo = key
            else:
                for base, aliases in alias_map.items():
                    if base in campos_norm and key in aliases:
                        campo = base
                        break
            if campo:
                for offset in range(1, 3):
                    if i + offset >= len(self.lines):
                        break
                    value = self.lines[i + offset].get("Text", "")
                    if normalize_key(value) in campos_norm:
                        continue
                    if campo not in self.field_dict:
                        self.field_dict[campo] = value
                    i += offset + 1
                    break
                else:
                    i += 1
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
                    if campo not in self.field_dict:
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
