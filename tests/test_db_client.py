import sys
from unittest.mock import MagicMock
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.modules.setdefault('sqlalchemy', MagicMock())
sys.modules.setdefault('sqlalchemy.orm', MagicMock())
sys.modules.setdefault('sqlalchemy.dialects', MagicMock())
sys.modules.setdefault('sqlalchemy.dialects.postgresql', MagicMock())
sys.modules.setdefault('services.db_models', MagicMock())

from web.services import db_client  # noqa: E402
from web.services.db_client import _extract, DatabaseClient  # noqa: E402


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


def test_movil_from_celular(monkeypatch):
    """telefono_movil uses telefono_celular when provided."""
    monkeypatch.setattr(DatabaseClient, "_ensure_columns", lambda self: None)
    mock_model = MagicMock()
    monkeypatch.setattr(db_client, "CreditApplication", mock_model)
    db = DatabaseClient()
    session_mock = MagicMock()
    db.SessionLocal = MagicMock(return_value=session_mock)

    db.save_form("credito_personal", {"telefono_celular": "777"}, None)

    assert mock_model.call_args.kwargs["telefono_movil"] == "777"


def test_casa_field(monkeypatch):
    """telecono_casa uses telefono_casa when provided."""
    monkeypatch.setattr(DatabaseClient, "_ensure_columns", lambda self: None)
    mock_model = MagicMock()
    monkeypatch.setattr(db_client, "CreditApplication", mock_model)
    db = DatabaseClient()
    session_mock = MagicMock()
    db.SessionLocal = MagicMock(return_value=session_mock)

    db.save_form("credito_personal", {"telefono_casa": "123"}, None)

    assert mock_model.call_args.kwargs["telecono_casa"] == "123"


def test_store_both_phone_numbers(monkeypatch):
    """Both phone numbers are passed to the model."""
    monkeypatch.setattr(DatabaseClient, "_ensure_columns", lambda self: None)
    mock_model = MagicMock()
    monkeypatch.setattr(db_client, "CreditApplication", mock_model)
    db = DatabaseClient()
    session_mock = MagicMock()
    db.SessionLocal = MagicMock(return_value=session_mock)

    fields = {"telefono_celular": "777", "telefono_casa": "555"}
    db.save_form("credito_personal", fields, None)

    kwargs = mock_model.call_args.kwargs
    assert kwargs["telefono_movil"] == "777"
    assert kwargs["telecono_casa"] == "555"


