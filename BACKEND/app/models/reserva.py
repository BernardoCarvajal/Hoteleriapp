from pydantic import BaseModel, Field, validator, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum

class EstadoReserva(str, Enum):
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"
    COMPLETADA = "completada"

class EstadoPago(str, Enum):
    PENDIENTE = "pendiente"
    PARCIAL = "parcial"
    COMPLETADO = "completado"
    REEMBOLSADO = "reembolsado"

class MetodoPago(str, Enum):
    TARJETA = "tarjeta"
    TRANSFERENCIA = "transferencia"
    EFECTIVO = "efectivo"
    PAYPAL = "paypal"

class ConsultaDisponibilidad(BaseModel):
    fecha_llegada: date
    fecha_salida: date
    num_huespedes: int = Field(..., gt=0)
    tipo_habitacion_id: Optional[int] = None

    @field_validator('fecha_salida')
    def fecha_salida_debe_ser_posterior(cls, v, values):
        if 'fecha_llegada' in values.data and v <= values.data['fecha_llegada']:
            raise ValueError('La fecha de salida debe ser posterior a la de llegada')
        return v

class HabitacionDisponible(BaseModel):
    id: int
    numero: str
    tipo: str
    capacidad: int
    precio_por_noche: float
    descripcion: Optional[str] = None

class DetalleReservaCreate(BaseModel):
    habitacion_id: int

class ReservaCreate(BaseModel):
    fecha_inicio: date
    fecha_fin: date
    numero_huespedes: int = Field(..., gt=0)
    detalles: List[DetalleReservaCreate]

    @field_validator('fecha_fin')
    def fecha_fin_debe_ser_posterior(cls, v, values):
        if 'fecha_inicio' in values.data and v <= values.data['fecha_inicio']:
            raise ValueError('La fecha de fin debe ser posterior a la de inicio')
        return v

class CalculoCosto(BaseModel):
    fecha_inicio: date
    fecha_fin: date
    habitaciones: List[int]
    
    @field_validator('fecha_fin')
    def fecha_fin_debe_ser_posterior(cls, v, values):
        if 'fecha_inicio' in values.data and v <= values.data['fecha_inicio']:
            raise ValueError('La fecha de fin debe ser posterior a la de inicio')
        return v

class CostoReserva(BaseModel):
    subtotal: float
    impuestos: float
    total: float
    desglose: Dict[str, Any]

class PagoCreate(BaseModel):
    reserva_id: int
    monto: float = Field(..., gt=0)
    metodo_pago: MetodoPago
    referencia_pago: Optional[str] = None

class Pago(PagoCreate):
    id: int
    fecha_pago: datetime
    estado: EstadoPago
    
    class Config:
        from_attributes = True

class DetalleReserva(BaseModel):
    id: int
    habitacion_id: int
    precio_por_noche: float
    
    class Config:
        from_attributes = True

class Reserva(BaseModel):
    id: int
    usuario_id: int
    fecha_inicio: date
    fecha_fin: date
    numero_huespedes: int
    estado: EstadoReserva
    codigo_reserva: str
    fecha_creacion: datetime
    notas: Optional[str] = None
    detalles: List[DetalleReserva] = []
    pagos: List[Pago] = []
    
    class Config:
        from_attributes = True 