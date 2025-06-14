import sys
from pathlib import Path
import types
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

alias_data = {
    "campo_prueba": ["Campo Prueba", "campo.prueba", "cám po prueba"],
    "check_option": ["Opción"],
}

def dummy_init(self, alias_file):
    from services.utils.normalization import normalize_key
    self.aliases = {
        normalize_key(k): [normalize_key(a) for a in v]
        for k, v in alias_data.items()
    }

@pytest.fixture
def alias_cls(monkeypatch):
    monkeypatch.setitem(sys.modules, "yaml", types.SimpleNamespace(safe_load=lambda f: {}))
    from services.field_correctors.alias_mapper import AliasMapper
    monkeypatch.setattr(AliasMapper, "__init__", dummy_init)
    return AliasMapper


def test_alias_mapper_normalization_get(alias_cls):
    mapper = alias_cls(None)
    fields = {"Campo Prueba": "valor"}
    assert mapper.get(fields, "campo_prueba") == "valor"


def test_alias_mapper_normalization_checked(alias_cls):
    mapper = alias_cls(None)
    fields = {"Opción": "X"}
    assert mapper.get_checked(fields, ["check_option"]) == "check_option"


def test_basic_cleaner_placeholder():
    from services.field_correctors.basic_cleaner import BasicFieldCorrector
    cleaner = BasicFieldCorrector()
    assert cleaner.correct("any", "VALUE_NOT_FOUND") is None
