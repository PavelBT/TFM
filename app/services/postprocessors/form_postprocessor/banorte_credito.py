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

    def process(self, raw_fields: dict, layout: dict | None = None) -> dict:
        """Clean generic fields and integrate checklist values.

        Parameters
        ----------
        raw_fields: dict
            Campos extraidos directamente del OCR.
        layout: dict, optional
            Datos adicionales obtenidos del layout parser (no utilizado por ahora).
        """

        cleaned = super().process(raw_fields)
        checklist = cleaned.pop("checklist", [])
        if isinstance(checklist, list):
            for key in checklist:
                label = self.CHECKLIST_MAP.get(key)
                if label:
                    cleaned[label] = key
        return cleaned
