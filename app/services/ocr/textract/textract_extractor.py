from typing import Dict, List
import unicodedata
import re

class TextractFullExtractor:
    def __init__(self, blocks: List[Dict]):
        self.blocks = blocks
        self.block_map = {block["Id"]: block for block in blocks if "Id" in block}
        self.key_map = {}
        self.value_map = {}
        self.field_dict = {}
        self.lines = [block for block in blocks if block["BlockType"] == "LINE"]
        self.selection_elements = [block for block in blocks if block["BlockType"] == "SELECTION_ELEMENT"]

        for block in blocks:
            if block["BlockType"] == "KEY_VALUE_SET":
                if "KEY" in block.get("EntityTypes", []):
                    self.key_map[block["Id"]] = block
                elif "VALUE" in block.get("EntityTypes", []):
                    self.value_map[block["Id"]] = block

    def extract(self) -> Dict[str, str]:
        used_value_ids = set()

        # 1. Extraer claves y valores de los KEY_VALUE_SET
        for key_block_id, key_block in self.key_map.items():
            key_text = self._get_text(key_block)
            if not key_text.strip():
                continue

            values = []
            for rel in key_block.get("Relationships", []):
                if rel["Type"] == "VALUE":
                    for value_id in rel["Ids"]:
                        value_block = self.value_map.get(value_id)
                        if value_block:
                            value_text = self._get_text(value_block)
                            values.append(value_text)
                            used_value_ids.add(value_id)

            self.field_dict[self._normalize_key(key_text)] = " | ".join(values)

        # 2. Agregar líneas sueltas tipo "clave: valor"
        for block in self.lines:
            text = block.get("Text", "")
            if ":" in text:
                key, value = map(str.strip, text.split(":", 1))
                if key and self._normalize_key(key) not in self.field_dict:
                    self.field_dict[self._normalize_key(key)] = value

        # 3. Agrupar líneas consecutivas campo-valor
        self._extract_consecutive_fields()

        # 4. Detectar checkboxes en campos conocidos
        self._extract_checkboxes()

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

    def _normalize_key(self, key: str) -> str:
        # Quitar acentos, minúsculas, quitar paréntesis y espacios extra
        key = unicodedata.normalize('NFKD', key).encode('ascii', 'ignore').decode('ascii')
        key = key.lower()
        key = re.sub(r'\(.*?\)', '', key)
        key = re.sub(r'[^a-z0-9 ]', '', key)
        return key.strip()

    def _extract_consecutive_fields(self):
        # Lista de campos conocidos (puedes expandirla)
        campos = [
            "nombre(s) (sin abreviaturas)", "apellido paterno", "apellido materno",
            "fecha de nacimiento", "pais de nacimiento", "nacionalidad", "genero",
            "telefono de casa", "telefono celular", "e-mail", "tipo de identificacion",
            "folio", "estado civil", "regimen matrimonial", "domicilio (calle y numero exterior e interior)",
            "colonia/urbanizacion", "delegacion/municipio/demarcacion politica", "ciudad/poblacion",
            "entidad federativa/estado", "pais", "cp", "anos de residencia"
        ]
        campos_norm = [self._normalize_key(c) for c in campos]

        i = 0
        while i < len(self.lines) - 1:
            key = self._normalize_key(self.lines[i].get("Text", ""))
            value = self.lines[i+1].get("Text", "")
            if key in campos_norm and self._normalize_key(value) not in campos_norm:
                if key not in self.field_dict:
                    self.field_dict[key] = value
                i += 2
            else:
                i += 1

    def _extract_checkboxes(self):
        # Busca SELECTION_ELEMENT seleccionados y asocia a la línea más cercana
        selected_ids = {block["Id"] for block in self.selection_elements if block.get("SelectionStatus") == "SELECTED"}
        for line in self.lines:
            rels = line.get("Relationships", [])
            for rel in rels:
                if rel["Type"] == "CHILD":
                    for child_id in rel["Ids"]:
                        if child_id in selected_ids:
                            # Asocia la opción seleccionada al campo anterior
                            text = line.get("Text", "")
                            idx = self.lines.index(line)
                            if idx > 0:
                                campo = self._normalize_key(self.lines[idx-1].get("Text", ""))
                                if campo and campo not in self.field_dict:
                                    self.field_dict[campo] = text