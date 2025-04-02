from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base

class EstadoReserva(enum.Enum):
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"
    COMPLETADA = "completada"

class EstadoPago(enum.Enum):
    PENDIENTE = "pendiente"
    PARCIAL = "parcial"
    COMPLETADO = "completado"
    REEMBOLSADO = "reembolsado"

class ReservaORM(Base):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime, nullable=False)
    numero_huespedes = Column(Integer, nullable=False)
    estado = Column(String(20), nullable=False, default=EstadoReserva.PENDIENTE.value)
    codigo_reserva = Column(String(20), unique=True, nullable=False, index=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    notas = Column(Text, nullable=True)
    
    # Relación con usuario (muchos a uno)
    usuario = relationship("UserORM", back_populates="reservas")
    
    # Relación con detalles de reserva (uno a muchos)
    detalles = relationship("DetalleReservaORM", back_populates="reserva", cascade="all, delete-orphan")
    
    # Relación con pagos (uno a muchos)
    pagos = relationship("PagoORM", back_populates="reserva", cascade="all, delete-orphan")

class DetalleReservaORM(Base):
    __tablename__ = "detalles_reserva"

    id = Column(Integer, primary_key=True, index=True)
    reserva_id = Column(Integer, ForeignKey("reservas.id"), nullable=False)
    habitacion_id = Column(Integer, ForeignKey("habitaciones.id"), nullable=False)
    precio_por_noche = Column(Float, nullable=False)
    
    # Relación con reserva (muchos a uno)
    reserva = relationship("ReservaORM", back_populates="detalles")
    
    # Relación con habitación (muchos a uno)
    habitacion = relationship("HabitacionORM", back_populates="reservas")

class PagoORM(Base):
    __tablename__ = "pagos"

    id = Column(Integer, primary_key=True, index=True)
    reserva_id = Column(Integer, ForeignKey("reservas.id"), nullable=False)
    monto = Column(Float, nullable=False)
    fecha_pago = Column(DateTime, default=datetime.utcnow)
    estado = Column(String(20), nullable=False, default=EstadoPago.PENDIENTE.value)
    metodo_pago = Column(String(50), nullable=False)
    referencia_pago = Column(String(100), nullable=True)
    
    # Relación con reserva (muchos a uno)
    reserva = relationship("ReservaORM", back_populates="pagos") 