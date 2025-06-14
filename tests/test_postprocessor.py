import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from services.postprocessors.generic_postprocessor import GenericPostProcessor


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
