import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from services.postprocessors.basic_postprocessor import BasicPostProcessor


def test_basic_postprocessor():
    processor = BasicPostProcessor()
    raw = {
        "Folio": "123",
        "Nombre": "Juan",
        "Email": "usuario@example.com ",
        "Teléfono": "55-1234-5678",
    }
    result = processor.process(raw)
    assert result["folio"] == "123"
    assert result["nombre"] == "Juan"
    assert result["email"] == "usuario@example.com"
    assert result["telefono"] == "5512345678"
