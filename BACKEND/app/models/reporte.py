from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from enum import Enum

class TipoReporte(str, Enum):
    RESERVAS = "reservas"
    OCUPACION = "ocupacion"
    INGRESOS = "ingresos"
    CLIENTES = "clientes"

class FiltroReporteReservas(BaseModel):
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    estado: Optional[str] = None
    cliente_id: Optional[int] = None

class ReporteReserva(BaseModel):
    id: int
    codigo_reserva: str
    cliente: str
    fecha_inicio: date
    fecha_fin: date
    estado: str
    habitaciones: List[str]
    total_pagado: float
    total_pendiente: float

class ReporteReservas(BaseModel):
    total_reservas: int
    ingresos_totales: float
    ingresos_pendientes: float
    reservas: List[ReporteReserva]

class ReporteOcupacion(BaseModel):
    fecha_inicio: date
    fecha_fin: date
    ocupacion_porcentaje: float
    habitaciones_totales: int
    habitaciones_ocupadas: int
    habitaciones_disponibles: int
    desglose_por_tipo: Dict[str, Any]
    ocupacion_diaria: Dict[str, float] 