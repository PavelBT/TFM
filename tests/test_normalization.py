import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from services.utils.normalization import normalize_key


def test_normalize_key_preserves_underscore():
    assert normalize_key('nombre_y_puesto') == 'nombre_y_puesto'
