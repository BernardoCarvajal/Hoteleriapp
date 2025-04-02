from pydantic import BaseModel, Field
from typing import Optional, List

class TipoHabitacionBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50)
    descripcion: Optional[str] = None
    precio_base: float = Field(..., gt=0)
    capacidad: int = Field(..., gt=0)

class TipoHabitacionCreate(TipoHabitacionBase):
    pass

class TipoHabitacion(TipoHabitacionBase):
    id: int
    
    class Config:
        from_attributes = True

class HabitacionBase(BaseModel):
    numero: str = Field(..., min_length=1, max_length=10)
    piso: int = Field(..., ge=1)
    tipo_id: int
    esta_activa: bool = True
    notas: Optional[str] = None

class HabitacionCreate(HabitacionBase):
    pass

class HabitacionUpdate(BaseModel):
    numero: Optional[str] = Field(None, min_length=1, max_length=10)
    piso: Optional[int] = Field(None, ge=1)
    tipo_id: Optional[int] = None
    esta_activa: Optional[bool] = None
    notas: Optional[str] = None

class Habitacion(HabitacionBase):
    id: int
    tipo: Optional[TipoHabitacion] = None
    
    class Config:
        from_attributes = True 