import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from services.field_correctors.structured_cleaner import StructuredFieldCorrector


def test_structured_cleaner_groups_fields():
    raw = {
        "Nombre": "Juan",
        "Teléfono de casa": "5512345678",
        "Sueldo mensual": "$1,000",
        "12": "[X]",
        "Femenino": "[X]",
        "Soltero": "[X]",
        "Sociedad Conyugal": "[X]",
    }
    cleaner = StructuredFieldCorrector()
    result = cleaner.transform(raw)

    assert result["datos_personales"]["nombre"] == "Juan"
    assert result["contacto"]["teléfono de casa"] == "5512345678"
    assert result["finanzas"]["sueldo_mensual"] == "1000"
    assert result["plazo_credito"] == "12"
    assert result["genero"] == "Femenino"
    assert result["estado_civil"] == "Soltero"
    assert result["regimen_matrimonial"] == "Sociedad Conyugal"

