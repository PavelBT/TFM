import sys
from unittest.mock import MagicMock
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.modules.setdefault('sqlalchemy', MagicMock())
sys.modules.setdefault('sqlalchemy.orm', MagicMock())
sys.modules.setdefault('sqlalchemy.dialects', MagicMock())
sys.modules.setdefault('sqlalchemy.dialects.postgresql', MagicMock())
sys.modules.setdefault('services.db_models', MagicMock())

from web.services.db_client import _extract


def test_extract_with_spaces():
    fields = {
        "datos_personales": {
            "apellido paterno": "Perez",
            "apellido_materno": "Lopez",
        },
        "finanzas": {
            "monto solicitado": "1000"
        }
    }
    assert _extract(fields, "apellido_paterno") == "Perez"
    assert _extract(fields, "monto_solicitado") == "1000"

