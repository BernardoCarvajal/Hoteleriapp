from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Table, Text
from sqlalchemy.orm import relationship

from app.database import Base

class TipoHabitacionORM(Base):
    __tablename__ = "tipos_habitacion"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)
    descripcion = Column(Text, nullable=True)
    precio_base = Column(Float, nullable=False)
    capacidad = Column(Integer, nullable=False)
    
    # Relación con habitaciones (uno a muchos)
    habitaciones = relationship("HabitacionORM", back_populates="tipo")

class HabitacionORM(Base):
    __tablename__ = "habitaciones"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(10), unique=True, nullable=False)
    piso = Column(Integer, nullable=False)
    tipo_id = Column(Integer, ForeignKey("tipos_habitacion.id"), nullable=False)
    esta_activa = Column(Boolean, default=True)
    notas = Column(Text, nullable=True)
    
    # Relación con tipo de habitación (muchos a uno)
    tipo = relationship("TipoHabitacionORM", back_populates="habitaciones")
    
    # Relación con reservas (uno a muchos)
    reservas = relationship("DetalleReservaORM", back_populates="habitacion") 