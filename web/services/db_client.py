import os
from typing import Any, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from services.utils.logger import get_logger
from services.utils.normalization import normalize_key, parse_money, parse_date
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
        table = CreditApplication.__tablename__
        columns = {col["name"] for col in inspector.get_columns(table)}
        statements = []
        if "email" not in columns:
            statements.append(f"ALTER TABLE {table} ADD COLUMN email VARCHAR")
        if "telefono_movil" not in columns:
            statements.append(f"ALTER TABLE {table} ADD COLUMN telefono_movil VARCHAR")
        if "telecono_casa" not in columns:
            statements.append(f"ALTER TABLE {table} ADD COLUMN telecono_casa VARCHAR")
        if "plazo_credito" not in columns:
            statements.append(f"ALTER TABLE {table} ADD COLUMN plazo_credito VARCHAR")

        if statements:
            with self.engine.begin() as conn:
                for stmt in statements:
                    conn.execute(text(stmt))

    def list_applications(self, form_type: str = "credito_personal") -> list:
        """Return stored credit applications for the given form type."""
        session: Session = self.SessionLocal()
        try:
            return (
                session.query(CreditApplication)
                .filter(CreditApplication.tipo_credito == form_type)
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
                telefono_movil=_extract(fields, "telefono_movil")
                or _extract(fields, "telefono_celular"),
                telecono_casa=_extract(fields, "telecono_casa")
                or _extract(fields, "telefono_casa"),
                fecha_nacimiento=parse_date(
                    _extract(fields, "fecha_nacimiento") or ""
                ),
                monto_solicitado=parse_money(
                    _extract(fields, "monto_solicitado")
                ),
                ingresos_mensuales=parse_money(
                    _extract(fields, "ingresos_mensuales")
                ),
                plazo_credito=
                    _extract(fields, "plazo_credito")
                    or _extract(fields, "plazo_meses")
                    or _extract(fields, "plazo_anios"),
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
