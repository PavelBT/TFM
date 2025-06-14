import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from services.field_correctors.basic_cleaner import BasicFieldCorrector


def test_basic_cleaner_placeholder():
    cleaner = BasicFieldCorrector()
    assert cleaner.correct("any", "VALUE_NOT_FOUND") is None


def test_basic_cleaner_unchecked_box():
    cleaner = BasicFieldCorrector()
    assert cleaner.correct("any", "[ ]") is None


def test_basic_cleaner_not_selected_keyword():
    cleaner = BasicFieldCorrector()
    assert cleaner.correct("any", "NOT_SELECTED") is None


def test_basic_cleaner_currency():
    cleaner = BasicFieldCorrector()
    assert cleaner.correct("monto solicitado", "$100,000.00") == "100000.00"


def test_basic_cleaner_discard_long_key():
    cleaner = BasicFieldCorrector()
    assert cleaner.correct("Aviso de Privacidad y Politica de Datos", "test") is None
