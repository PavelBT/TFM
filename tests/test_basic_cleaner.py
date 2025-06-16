import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from services.field_correctors.basic_cleaner import BasicFieldCorrector


def test_basic_cleaner_email_normalization():
    cleaner = BasicFieldCorrector()
    assert (
        cleaner.correct("Email", "USUARIO@Example.com ")
        == "usuario@example.com"
    )


def test_basic_cleaner_phone_digits():
    cleaner = BasicFieldCorrector()
    assert cleaner.correct("Teléfono", "(55) 1234-5678") == "5512345678"


def test_basic_cleaner_amount_digits_only():
    cleaner = BasicFieldCorrector()
    assert cleaner.correct("Monto", "$1,234") == "1234"


def test_basic_cleaner_name_capitalization():
    cleaner = BasicFieldCorrector()
    assert cleaner.correct("Nombre", "juan perez") == "Juan Perez"

