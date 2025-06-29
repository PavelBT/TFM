from datetime import datetime
import uuid

from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Numeric,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class CreditApplication(Base):
    __tablename__ = 'credit_applications'

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String, unique=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=text('NOW()'))
    updated_at = Column(DateTime(timezone=True), server_default=text('NOW()'), onupdate=datetime.utcnow)

    tipo_credito = Column(String)
    nombre = Column(String)
    apellido_paterno = Column(String)
    apellido_materno = Column(String)
    rfc = Column(String)
    curp = Column(String)
    email = Column(String)
    telefono_celular = Column(String)
    telefono_casa = Column(String)
    fecha_nacimiento = Column(Date)
    monto_solicitado = Column(Numeric(12, 2))
    ingresos_mensuales = Column(Numeric(12, 2))
    riesgo_score = Column(Numeric(6, 2))
    riesgo_clase = Column(String)
    extra_data = Column(JSONB)
    file_url = Column(String)
    status = Column(String, default='nuevo')

