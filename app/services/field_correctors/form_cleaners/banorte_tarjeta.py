# Ruta: services/form_cleaners/banorte_tarjeta.py

from typing import Dict

class BanorteTarjetaFormProcessor:
    """
    Organización y limpieza específica para el formulario:
    'SOLICITUD DE TARJETA DE CRÉDITO'
    """

    def transform(self, structured: Dict) -> Dict:
        # Normalizar nombres
        dp = structured.get("datos_personales", {})
        for key in ["nombre", "apellido_paterno", "apellido_materno"]:
            if key in dp:
                dp[key] = dp[key].title()

        # Normalizar campo de límite solicitado
        if "finanzas" in structured and "limite_credito" in structured["finanzas"]:
            raw = structured["finanzas"]["limite_credito"]
            limite = "".join(c for c in raw if c.isdigit())
            structured["finanzas"]["limite_credito"] = limite

        # Asegurar género consistente
        genero = structured.get("genero", "").lower()
        if "masc" in genero:
            structured["genero"] = "Masculino"
        elif "fem" in genero:
            structured["genero"] = "Femenino"

        # Estado civil si aplica
        ec = structured.get("estado_civil", "").lower()
        for clave, valor in {
            "soltero": "Soltero",
            "casado": "Casado",
            "unión": "Unión libre",
            "divorciado": "Divorciado",
            "viudo": "Viudo"
        }.items():
            if clave in ec:
                structured["estado_civil"] = valor
                break

        return structured