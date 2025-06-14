import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

sys.modules.setdefault("yaml", types.SimpleNamespace(safe_load=lambda f: {}))

from services.postprocessors.form_postprocessor.banorte_credito import BanorteCreditoPostProcessor
from services.field_correctors import alias_mapper
from services.utils.normalization import normalize_key

alias_data = {
    "folio": ["folio"],
    "nombre": ["nombres_sin_abreviaturas"],
    "apellido_paterno": ["apellido_paterno"],
    "estado_civil.casado (a)": ["casado"],
}

def dummy_init(self, alias_file):
    self.aliases = {
        normalize_key(k): [normalize_key(a) for a in v]
        for k, v in alias_data.items()
    }

alias_mapper.AliasMapper.__init__ = dummy_init


def test_banorte_credito_postprocessor():
    processor = BanorteCreditoPostProcessor()
    raw = {
        "Folio": "123",
        "Nombre(s) (sin abreviaturas)": "Juan",
        "Apellido Paterno": "Perez",
        "Casado (a)": "[X]",
    }
    result = processor.process(raw)
    assert result["datos_control"]["folio"] == "123"
    assert result["datos_personales"]["estado_civil"] == "estado_civil.casado (a)"
