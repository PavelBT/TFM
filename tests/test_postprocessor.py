import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from services.postprocessors.generic_postprocessor import GenericPostProcessor
from services.postprocessors.form_postprocessor.banorte_credito import BanorteCreditoPostProcessor


def test_generic_postprocessor():
    processor = GenericPostProcessor()
    raw = {
        "Folio": "123",
        "Nombre(s) (sin abreviaturas)": "Juan",
        "Apellido Paterno": "Perez",
        "Casado (a)": "[X]",
        "12": "[X]",
    }
    result = processor.process(raw)
    assert result["folio"] == "123"
    assert result["nombre"] == "Juan"
    assert result["apellido_paterno"] == "Perez"
    assert "casado" in result["checklist"]
    assert "12" in result["checklist"]


def test_generic_postprocessor_removes_checkbox_fields():
    processor = GenericPostProcessor()
    raw = {"Soltero": "[X]", "Folio": "1"}
    result = processor.process(raw)
    assert "soltero" not in result
    assert "soltero" in result["checklist"]

def test_banorte_postprocessor_checklist():
    processor = BanorteCreditoPostProcessor()
    raw = {
        "12": "[X]",
        "24": "[X]",
        "48": "[X]",
        "Femenino": "[X]",
        "Soltero": "[X]",
        "Propia": "[X]",
        "Asalariado": "[X]",
        "No": "[X]",
    }
    result = processor.process(raw)
    assert "checklist" not in result
    assert result["plazo_de_credito"] == "48"
    assert result["genero"] == "femenino"
    assert result["estado_civil"] == "soltero"
    assert result["vivienda"] == "propia"
    assert result["tipo_de_empleo"] == "asalariado"
    assert result["politicamente_expuesto"] == "no"


def test_banorte_postprocessor_extract_email():
    processor = BanorteCreditoPostProcessor()
    raw = {
        "informacion_personal": [
            "Teléfono Celular",
            "4432222222",
            "E-mail",
            "4431111111",
            "usuario@example.com",
            "Tipo de Identificación",
            "INE",
        ]
    }
    result = processor.process(raw)
    assert result["email"] == "usuario@example.com"


def test_banorte_postprocessor_preserves_existing_field():
    processor = BanorteCreditoPostProcessor()
    raw = {
        "email": "orig@example.com",
        "informacion_personal": [
            "E-mail",
            "otro@example.com",
        ],
    }
    result = processor.process(raw)
    assert result["email"] == "orig@example.com"

