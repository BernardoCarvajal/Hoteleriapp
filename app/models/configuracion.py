from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class CodigoIdioma(str, Enum):
    ESPANOL = "es"
    INGLES = "en"

class IdiomaBase(BaseModel):
    codigo: str = Field(..., min_length=2, max_length=5)
    nombre: str = Field(..., min_length=2, max_length=50)
    es_activo: bool = True
    es_default: bool = False

class IdiomaCreate(IdiomaBase):
    pass

class Idioma(IdiomaBase):
    id: int
    
    class Config:
        from_attributes = True

class ConfiguracionBase(BaseModel):
    clave: str = Field(..., min_length=3, max_length=50)
    valor: str = Field(..., min_length=1, max_length=500)
    descripcion: Optional[str] = Field(None, max_length=200)

class ConfiguracionCreate(ConfiguracionBase):
    pass

class ConfiguracionUpdate(BaseModel):
    valor: str = Field(..., min_length=1, max_length=500)
    descripcion: Optional[str] = Field(None, max_length=200)

class Configuracion(ConfiguracionBase):
    id: int
    fecha_actualizacion: datetime
    
    class Config:
        from_attributes = True

class CambioIdioma(BaseModel):
    codigo: CodigoIdioma 