from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime

class RoleBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=50)
    descripcion: Optional[str] = Field(None, max_length=200)

class RoleCreate(RoleBase):
    pass

class Role(RoleBase):
    id: int
    
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    apellido: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    telefono: Optional[str] = Field(None, max_length=20)
    documento_identidad: Optional[str] = Field(None, max_length=20)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    apellido: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    telefono: Optional[str] = Field(None, max_length=20)
    documento_identidad: Optional[str] = Field(None, max_length=20)
    es_activo: Optional[bool] = None

class User(UserBase):
    id: int
    es_activo: bool
    fecha_registro: datetime
    roles: List[Role] = []
    
    class Config:
        from_attributes = True

class UserWithRoles(User):
    roles: List[Role]

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None 