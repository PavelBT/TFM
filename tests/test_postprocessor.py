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


def test_generic_alias_and_stray_si_no():
    processor = GenericPostProcessor()
    raw = {"empresa_donde_trabajo": "CNDH", "Si": "VALUE_NOT_FOUND"}
    result = processor.process(raw)
    assert "empresa" in result
    assert "si" not in result



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
    assert result["plazo_de_credito"] == "12"
    assert result["genero"] == "femenino"
    assert result["estado_civil"] == "soltero"
    assert result["vivienda"] == "propia"
    assert result["tipo_de_empleo"] == "asalariado"
    assert result["politicamente_expuesto"] == "no"


def test_banorte_plazo_18():
    processor = BanorteCreditoPostProcessor()
    raw = {"18": "[X]"}
    result = processor.process(raw)
    assert result["plazo_de_credito"] == "18"
    assert "checklist" not in result


def test_banorte_infer_plazo_from_section():
    processor = BanorteCreditoPostProcessor()
    raw = {"informacion_del_credito": ["Monto", "1000", "18", "Meses"]}
    result = processor.process(raw)
    assert result["plazo_de_credito"] == "18"


def test_banorte_split_full_name():
    processor = BanorteCreditoPostProcessor()
    raw = {"Nombre_y_Apellido": "Claudia Gonzalez Reyes"}
    result = processor.process(raw)
    assert result["nombre"] == "Claudia"
    assert result["apellido_paterno"] == "Gonzalez"
    assert result["apellido_materno"] == "Reyes"

