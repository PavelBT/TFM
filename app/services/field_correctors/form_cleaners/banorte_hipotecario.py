# Ruta: services/form_cleaners/banorte_hipotecario.py

from typing import Dict

class BanorteHipotecarioFormProcessor:
    """
    Organización y limpieza específica para el formulario:
    'SOLICITUD DE CRÉDITO HIPOTECARIO'
    """

    def transform(self, structured: Dict) -> Dict:
        # Normalización básica de nombres si existen
        dp = structured.get("datos_personales", {})
        for key in ["nombre", "apellido_paterno", "apellido_materno"]:
            if key in dp:
                dp[key] = dp[key].title()

        # Homogeneizar estado civil
        ec = structured.get("estado_civil", "").lower()
        estados = {
            "soltero": "Soltero",
            "casado": "Casado",
            "viudo": "Viudo",
            "divorciado": "Divorciado",
            "unión": "Unión libre"
        }
        for clave, valor in estados.items():
            if clave in ec:
                structured["estado_civil"] = valor
                break

        # Limpieza numérica de ingresos, si existen
        finanzas = structured.get("finanzas", {})
        for campo in ["ingreso_bruto", "ingreso_neto"]:
            if campo in finanzas:
                bruto = "".join(c for c in finanzas[campo] if c.isdigit())
                finanzas[campo] = bruto

        # Transformación o agrupaciones específicas futuras pueden agregarse aquí

        return structured