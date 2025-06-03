# Ruta: services/field_correctors/especificos/banorte_credito.py

from typing import Dict

class BanorteCreditoFormProcessor:
    """
    Aplica reglas de organización y corrección específicas para el formulario
    'Solicitud Crédito Personal Banorte'. Se ejecuta sobre la salida estructurada genérica.
    """

    def transform(self, structured: Dict) -> Dict:
        # Normalización de nombres propios
        if "datos_personales" in structured:
            dp = structured["datos_personales"]
            for key in ["nombre", "apellido_paterno", "apellido_materno"]:
                if key in dp:
                    dp[key] = dp[key].title()

        # Limpieza del monto solicitado
        if "finanzas" in structured and "monto_solicitado" in structured["finanzas"]:
            raw = structured["finanzas"]["monto_solicitado"]
            monto = "".join(c for c in raw if c.isdigit())
            structured["finanzas"]["monto_solicitado"] = monto

        # Homogeneizar género
        genero = structured.get("genero", "").lower()
        if "masc" in genero:
            structured["genero"] = "Masculino"
        elif "fem" in genero:
            structured["genero"] = "Femenino"

        # Homogeneizar estado civil
        ec = structured.get("estado_civil", "").lower()
        mapping = {
            "union": "Unión libre",
            "soltero": "Soltero",
            "casado": "Casado",
            "divorciado": "Divorciado",
            "viudo": "Viudo"
        }
        for key in mapping:
            if key in ec:
                structured["estado_civil"] = mapping[key]
                break

        return structured