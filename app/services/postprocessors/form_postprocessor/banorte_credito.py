from services.postprocessors.generic_postprocessor import GenericPostProcessor


class BanorteCreditoPostProcessor(GenericPostProcessor):
    """Postprocesador especializado para formularios de crédito Banorte."""

    CHECKLIST_MAP = {
        "12": "plazo_de_credito",
        "18": "plazo_de_credito",
        "24": "plazo_de_credito",
        "36": "plazo_de_credito",
        "48": "plazo_de_credito",
        "60": "plazo_de_credito",
        "femenino": "genero",
        "masculino": "genero",
        "soltero": "estado_civil",
        "casado": "estado_civil",
        "union_libre": "estado_civil",
        "propia": "vivienda",
        "rentada": "vivienda",
        "hipotecada": "vivienda",
        "asalariado": "tipo_de_empleo",
        "honorarios": "tipo_de_empleo",
        "si": "politicamente_expuesto",
        "no": "politicamente_expuesto",
    }

    SECTION_KEYS = [
        "informacion_personal",
        "domicilio",
        "empleo",
    ]

    FIELD_PATTERNS = {
        "nombre": ["nombre"],
        "apellido_paterno": ["apellido paterno"],
        "apellido_materno": ["apellido materno"],
        "delegacion_municipio": ["delegacion", "municipio"],
        "cp": ["c.p", "codigo postal"],
        "email": ["e-mail", "email", "correo"],
        "telefono_de_casa": ["telefono de casa"],
        "telefono_celular": ["telefono celular"],
        "sueldo_mensual": ["sueldo mensual"],
        "regimen_matrimonial": ["regimen matrimonial"],
        "otros_ingresos": ["otros ingresos", "fuente de otros ingresos"],
        "puesto_en_la_empresa": ["puesto"],
    }

    GENERIC_KEYS = {"mes", "año", "anio", "nombre", "sexo"}

    ADDRESS_PATTERNS = {
        "cp": ["c.p", "codigo postal", "cp"],
        "colonia": ["colonia"],
        "pais": ["pais"],
        "estado": ["estado"],
    }

    NUMERIC_PLAZOS = {"12", "18", "24", "36", "48", "60"}

    def _infer_plazo_from_section(self, raw_fields: dict) -> str | None:
        lines = raw_fields.get("informacion_del_credito")
        if not isinstance(lines, list):
            return None
        matches = [l.strip() for l in lines if l.strip() in self.NUMERIC_PLAZOS]
        if len(matches) == 1:
            return matches[0]
        return None

    def _extract_address_fields(self, lines: list[str]) -> dict:
        extracted: dict = {}
        i = 0
        while i < len(lines) - 1:
            key = lines[i].strip().lower()
            val = lines[i + 1].strip()
            for field, patterns in self.ADDRESS_PATTERNS.items():
                if any(p in key for p in patterns) and val:
                    extracted[field] = val
                    i += 1
                    break
            i += 1
        return extracted

    def _extract_from_sections(self, raw_fields: dict) -> dict:
        extracted: dict = {}
        for section in self.SECTION_KEYS:
            lines = raw_fields.get(section)
            if not isinstance(lines, list):
                continue
            i = 0
            if section == "domicilio":
                extracted.update(self._extract_address_fields(lines))
            while i < len(lines) - 1:
                key = lines[i].strip().lower()
                val = lines[i + 1].strip()
                if key in self.GENERIC_KEYS and val:
                    field_name = f"{section}_{key}"
                    extracted[field_name] = val
                    i += 1
                    continue
                for field, patterns in self.FIELD_PATTERNS.items():
                    if any(p in key for p in patterns) and val:
                        extracted[field] = val
                        i += 1
                        break
                i += 1
        return extracted
    def process(self, raw_fields: dict, layout: dict | None = None) -> dict:
        """Clean generic fields and integrate checklist values.

        Parameters
        ----------
        raw_fields: dict
            Campos extraidos directamente del OCR.
        layout: dict, optional
            Datos adicionales obtenidos del layout parser (no utilizado por ahora).
        """

        extracted = self._extract_from_sections(raw_fields)
        raw_fields.update(extracted)
        cleaned = super().process(raw_fields)
        checklist = cleaned.pop("checklist", [])
        if isinstance(checklist, list):
            for key in checklist:
                label = self.CHECKLIST_MAP.get(key)
                if label and label not in cleaned:
                    cleaned[label] = key

        if "plazo_de_credito" not in cleaned:
            plazo = self._infer_plazo_from_section(raw_fields)
            if plazo:
                cleaned["plazo_de_credito"] = plazo

        for key in list(cleaned.keys()):
            if "nombre_y_apellido" in key or "nombre_completo" in key:
                parts = self._split_full_name(cleaned.pop(key))
                for k, v in parts.items():
                    cleaned.setdefault(k, v)
        return cleaned

    def _split_full_name(self, full: str) -> dict:
        tokens = full.split()
        if len(tokens) == 2:
            return {"nombre": tokens[0], "apellido_paterno": tokens[1]}
        if len(tokens) >= 3:
            return {
                "nombre": tokens[0],
                "apellido_paterno": tokens[1],
                "apellido_materno": " ".join(tokens[2:]),
            }
        return {"nombre": full}
