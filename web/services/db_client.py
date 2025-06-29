import os
from typing import Any, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from services.utils.logger import get_logger
from services.db_models import Base, CreditApplication

DEFAULT_DB_URL = "postgresql+psycopg2://user:password@db:5432/ocrdata"


def _extract(fields: dict, key: str) -> Optional[Any]:
    """Recursively search a key in a nested dictionary."""
    if key in fields:
        return fields[key]
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
        self.SessionLocal = sessionmaker(bind=self.engine)

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
