import os
from typing import Any, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from services.utils.logger import get_logger
from services.utils.normalization import normalize_key
from services.db_models import Base, CreditApplication

DEFAULT_DB_URL = "postgresql+psycopg2://user:password@db:5432/ocrdata"


def _extract(fields: dict, key: str) -> Optional[Any]:
    """Recursively search a key in a nested dictionary."""
    if key in fields:
        return fields[key]

    normalized_target = normalize_key(key)

    for k, value in fields.items():
        if normalize_key(k) == normalized_target:
            return value

    for value in fields.values():
        if isinstance(value, dict):
            found = _extract(value, key)
            if found is not None:
                return found
    return None


class DatabaseClient:
    """Persist credit applications to the database."""

    def __init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__)
        database_url = os.getenv("DATABASE_URL", DEFAULT_DB_URL)
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self._ensure_columns()
        self.SessionLocal = sessionmaker(bind=self.engine)

    def _ensure_columns(self) -> None:
        """Create new columns if they are missing.

        This avoids crashes when the database schema predates new fields
        added in the model definition.
        """
        from sqlalchemy import inspect

        inspector = inspect(self.engine)
        columns = {col["name"] for col in inspector.get_columns("credit_applications")}
        statements = []
        if "email" not in columns:
            statements.append("ALTER TABLE credit_applications ADD COLUMN email VARCHAR")
        if "telefono_celular" not in columns:
            statements.append("ALTER TABLE credit_applications ADD COLUMN telefono_celular VARCHAR")
        if "telefono_casa" not in columns:
            statements.append("ALTER TABLE credit_applications ADD COLUMN telefono_casa VARCHAR")

        if statements:
            with self.engine.begin() as conn:
                for stmt in statements:
                    conn.execute(text(stmt))

    def list_applications(self) -> list[CreditApplication]:
        """Return all stored credit applications."""
        session: Session = self.SessionLocal()
        try:
            return (
                session.query(CreditApplication)
                .order_by(CreditApplication.id.desc())
                .all()
            )
        finally:
            session.close()

    def save_form(self, form_type: str, fields: dict, file_url: Optional[str] = None) -> None:
        session: Session = self.SessionLocal()
        try:
            record = CreditApplication(
                tipo_credito=form_type,
                nombre=_extract(fields, "nombre"),
                apellido_paterno=_extract(fields, "apellido_paterno"),
                apellido_materno=_extract(fields, "apellido_materno"),
                rfc=_extract(fields, "rfc"),
                curp=_extract(fields, "curp"),
                email=_extract(fields, "email"),
                telefono_celular=_extract(fields, "telefono_celular"),
                telefono_casa=_extract(fields, "telefono_casa"),
                fecha_nacimiento=_extract(fields, "fecha_nacimiento"),
                monto_solicitado=_extract(fields, "monto_solicitado"),
                ingresos_mensuales=_extract(fields, "ingresos_mensuales"),
                riesgo_score=_extract(fields, "riesgo_score"),
                riesgo_clase=_extract(fields, "riesgo_clase"),
                extra_data=fields,
                file_url=file_url,
                status="nuevo",
            )
            session.add(record)
            session.commit()
            self.logger.info("Saved credit application %s", record.uuid)
        except Exception as exc:  # pragma: no cover - minimal logging
            session.rollback()
            self.logger.error("Error saving application: %s", exc)
            raise
        finally:
            session.close()
