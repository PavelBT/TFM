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
    assert result["checklist"] == {
        "plazo_de_credito": "48",
        "genero": "femenino",
        "estado_civil": "soltero",
        "vivienda": "propia",
        "tipo_de_empleo": "asalariado",
        "politicamente_expuesto": "no",
    }

