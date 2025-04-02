from fastapi import APIRouter, HTTPException, status, Depends, Header
from typing import List, Optional
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os

from app.database import get_db
from app.models.user import (
    UserCreate, User, UserLogin, UserUpdate, Token, Role, UserWithRoles
)
from app.models.user_orm import UserORM, RoleORM

router = APIRouter()

# Configuración de JWT
SECRET_KEY = os.getenv("SECRET_KEY", "clave_super_secreta_para_desarrollo")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def crear_token_acceso(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Header(..., alias="Authorization"), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Eliminar prefijo "Bearer " si existe
        if token.startswith("Bearer "):
            token = token[7:]
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(UserORM).filter(UserORM.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user

async def get_admin_user(current_user: UserORM = Depends(get_current_user), db: Session = Depends(get_db)):
    user_roles = [role.nombre for role in current_user.roles]
    if "admin" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permisos insuficientes. Se requiere rol de administrador."
        )
    return current_user

# Endpoint para registro de clientes
@router.post("/registro", response_model=User, status_code=status.HTTP_201_CREATED)
async def registro_usuario(
    usuario: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Registrar un nuevo usuario (cliente)
    """
    # Verificar si el email ya existe
    usuario_existente = db.query(UserORM).filter(UserORM.email == usuario.email).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este email ya está registrado"
        )
    
    # Crear nuevo usuario
    hashed_password = generate_password_hash(usuario.password)
    
    # Por defecto, asignar rol de cliente
    rol_cliente = db.query(RoleORM).filter(RoleORM.nombre == "cliente").first()
    if not rol_cliente:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Rol 'cliente' no encontrado"
        )
    
    db_usuario = UserORM(
        nombre=usuario.nombre,
        apellido=usuario.apellido,
        email=usuario.email,
        password_hash=hashed_password,
        telefono=usuario.telefono,
        documento_identidad=usuario.documento_identidad,
        es_activo=True
    )
    
    db_usuario.roles.append(rol_cliente)
    
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    
    return db_usuario

# Endpoint para login de usuarios
@router.post("/login", response_model=Token)
async def login_usuario(
    datos_login: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login de usuario con JWT
    """
    # Buscar usuario por email
    usuario = db.query(UserORM).filter(UserORM.email == datos_login.email).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    # Verificar contraseña
    if not check_password_hash(usuario.password_hash, datos_login.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    # Verificar que el usuario esté activo
    if not usuario.es_activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inactivo"
        )
    
    # Crear token JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crear_token_acceso(
        data={"sub": str(usuario.id)},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint para registrar empleados (solo administradores)
@router.post("/empleados", response_model=UserWithRoles, status_code=status.HTTP_201_CREATED)
async def registro_empleado(
    usuario: UserCreate,
    _: UserORM = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Registrar un nuevo empleado (solo administradores)
    """
    # Verificar si el email ya existe
    usuario_existente = db.query(UserORM).filter(UserORM.email == usuario.email).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este email ya está registrado"
        )
    
    # Crear nuevo usuario
    hashed_password = generate_password_hash(usuario.password)
    
    # Asignar rol de empleado
    rol_empleado = db.query(RoleORM).filter(RoleORM.nombre == "empleado").first()
    if not rol_empleado:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Rol 'empleado' no encontrado"
        )
    
    db_usuario = UserORM(
        nombre=usuario.nombre,
        apellido=usuario.apellido,
        email=usuario.email,
        password_hash=hashed_password,
        telefono=usuario.telefono,
        documento_identidad=usuario.documento_identidad,
        es_activo=True
    )
    
    db_usuario.roles.append(rol_empleado)
    
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    
    return db_usuario

# Endpoint para asignar roles (solo administradores)
@router.put("/{usuario_id}/roles", response_model=UserWithRoles)
async def asignar_roles(
    usuario_id: int,
    roles_ids: List[int],
    _: UserORM = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Asignar roles a un usuario (solo administradores)
    """
    # Buscar usuario
    usuario = db.query(UserORM).filter(UserORM.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado"
        )
    
    # Obtener roles
    roles = db.query(RoleORM).filter(RoleORM.id.in_(roles_ids)).all()
    if len(roles) != len(roles_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uno o más roles no existen"
        )
    
    # Asignar roles
    usuario.roles = roles
    
    db.commit()
    db.refresh(usuario)
    
    return usuario 