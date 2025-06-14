from services.postprocessors.generic_postprocessor import GenericPostProcessor


class BanorteCreditoPostProcessor(GenericPostProcessor):
    """Postprocesador especializado para formularios de crédito Banorte."""

    CHECKLIST_MAP = {
        "12": "plazo_de_credito",
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

    def _extract_from_sections(self, raw_fields: dict) -> dict:
        extracted: dict = {}
        for section in self.SECTION_KEYS:
            lines = raw_fields.get(section)
            if not isinstance(lines, list):
                continue
            i = 0
            while i < len(lines) - 1:
                key = lines[i].strip().lower()
                val = lines[i + 1].strip()
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
                if label:
                    cleaned[label] = key
        return cleaned
