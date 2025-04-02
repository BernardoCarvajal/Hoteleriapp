from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base

# Tabla intermedia para la relación muchos a muchos entre usuarios y roles
user_role = Table(
    'user_role',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('usuarios.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

class UserORM(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(200), nullable=False)
    telefono = Column(String(20), nullable=True)
    documento_identidad = Column(String(20), nullable=True)
    es_activo = Column(Boolean, default=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    
    # Relación con roles (muchos a muchos)
    roles = relationship("RoleORM", secondary=user_role, back_populates="usuarios")
    
    # Relación con reservas (uno a muchos)
    reservas = relationship("ReservaORM", back_populates="usuario")

class RoleORM(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)
    descripcion = Column(String(200), nullable=True)
    
    # Relación con usuarios (muchos a muchos)
    usuarios = relationship("UserORM", secondary=user_role, back_populates="roles") 