import sys
from unittest.mock import MagicMock
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.modules.setdefault('sqlalchemy', MagicMock())
sys.modules.setdefault('sqlalchemy.orm', MagicMock())
sys.modules.setdefault('sqlalchemy.dialects', MagicMock())
sys.modules.setdefault('sqlalchemy.dialects.postgresql', MagicMock())
sys.modules.setdefault('services.db_models', MagicMock())

from web.services import db_client
from web.services.db_client import _extract, DatabaseClient


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


def test_save_form_hipotecario(monkeypatch):
    monkeypatch.setattr(DatabaseClient, "_ensure_columns", lambda self: None)
    mock_model = MagicMock()
    monkeypatch.setattr(db_client, "CreditApplication", mock_model)
    db = DatabaseClient()
    session_mock = MagicMock()
    db.SessionLocal = MagicMock(return_value=session_mock)
    db.save_form("credito_hipotecario", {"nombre": "Ana"}, None)
    mock_model.assert_called()
    session_mock.add.assert_called()


