from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base

class ConfiguracionORM(Base):
    __tablename__ = "configuraciones"

    id = Column(Integer, primary_key=True, index=True)
    clave = Column(String(50), unique=True, nullable=False, index=True)
    valor = Column(String(500), nullable=False)
    descripcion = Column(String(200), nullable=True)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class IdiomaORM(Base):
    __tablename__ = "idiomas"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(5), unique=True, nullable=False, index=True)
    nombre = Column(String(50), nullable=False)
    es_activo = Column(Boolean, default=True)
    es_default = Column(Boolean, default=False) 