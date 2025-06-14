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

    def process(self, raw_fields: dict) -> dict:
        cleaned = super().process(raw_fields)
        checklist = cleaned.get("checklist")
        if isinstance(checklist, list):
            labeled = {}
            for key in checklist:
                label = self.CHECKLIST_MAP.get(key)
                if label:
                    labeled[label] = key
            cleaned["checklist"] = labeled
        return cleaned
