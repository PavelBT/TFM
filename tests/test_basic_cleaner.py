import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from services.field_correctors.basic_cleaner import BasicFieldCorrector


def test_basic_cleaner_placeholder():
    cleaner = BasicFieldCorrector()
    assert cleaner.correct("any", "VALUE_NOT_FOUND") is None
