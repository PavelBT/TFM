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


def test_money_fields_are_parsed(monkeypatch):
    """Money fields are parsed but riesgo_score is not."""
    monkeypatch.setattr(DatabaseClient, "_ensure_columns", lambda self: None)
    mock_model = MagicMock()
    monkeypatch.setattr(db_client, "CreditApplication", mock_model)
    parse_mock = MagicMock(side_effect=lambda v: f"parsed-{v}")
    monkeypatch.setattr(db_client, "parse_money", parse_mock)

    db = DatabaseClient()
    session_mock = MagicMock()
    db.SessionLocal = MagicMock(return_value=session_mock)

    fields = {
        "monto_solicitado": "$1,000",
        "ingresos_mensuales": "2,000",
        "riesgo_score": "0.77",
    }
    db.save_form("credito_personal", fields, None)

    assert parse_mock.call_count == 2
    kwargs = mock_model.call_args.kwargs
    assert kwargs["monto_solicitado"] == "parsed-$1,000"
    assert kwargs["ingresos_mensuales"] == "parsed-2,000"
    assert kwargs["riesgo_score"] == "0.77"


def test_plazo_credito_fallback(monkeypatch):
    """plazo_credito uses plazo_meses or plazo_anios when provided."""
    monkeypatch.setattr(DatabaseClient, "_ensure_columns", lambda self: None)
    mock_model = MagicMock()
    monkeypatch.setattr(db_client, "CreditApplication", mock_model)
    db = DatabaseClient()
    session_mock = MagicMock()
    db.SessionLocal = MagicMock(return_value=session_mock)

    fields = {"informacion_credito": {"plazo_meses": "12"}}
    db.save_form("credito_personal", fields, None)
    assert mock_model.call_args.kwargs["plazo_credito"] == "12"

    fields = {"informacion_credito": {"plazo_anios": "8"}}
    db.save_form("credito_hipotecario", fields, None)
    assert mock_model.call_args.kwargs["plazo_credito"] == "8"


