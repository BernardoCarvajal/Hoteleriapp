from fastapi import APIRouter, HTTPException, status, Depends, Header, Security
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from app.database import get_db
from app.models.user import (
    UserCreate, User, UserLogin, UserUpdate, Token, Role, UserWithRoles
)
from app.models.user_orm import UserORM, RoleORM, user_role
from app.models.reserva_orm import ReservaORM, DetalleReservaORM, PagoORM, EstadoReserva
from app.models.habitacion_orm import HabitacionORM
from app.config import SECRET_KEY, ALGORITHM

# Definir modelos de respuesta
class JsonResponse(BaseModel):
    mensaje: str
    user_id: str
    email: str
    roles: str

class RolesResponse(BaseModel):
    roles: List[str]
    id: int
    email: str

router = APIRouter()

# Configurar el esquema de seguridad globalmente
security = HTTPBearer(auto_error=True, description="Bearer authentication token (JWT)")

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

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        print(f"Token recibido: {token[:20]}...")
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise credentials_exception
            
            print(f"ID de usuario extraído del token: {user_id}")
        except JWTError as e:
            print(f"Error al decodificar token: {str(e)}")
            raise credentials_exception
        
        user = db.query(UserORM).filter(UserORM.id == user_id).first()
        if user is None:
            print(f"Usuario con ID {user_id} no encontrado en la base de datos")
            raise credentials_exception
        
        print(f"Usuario autenticado: {user.email} (ID: {user.id})")
        return user
        
    except Exception as e:
        print(f"Error no esperado en autenticación: {str(e)}")
        raise credentials_exception

async def get_admin_user(current_user: UserORM = Security(get_current_user), db: Session = Depends(get_db)):
    user_roles = [role.nombre for role in current_user.roles]
    print(f"Usuario {current_user.id} ({current_user.email}) tiene roles: {user_roles}")
    if "admin" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permisos insuficientes. Se requiere rol de administrador."
        )
    return current_user

# Endpoint simple para probar la autenticación
@router.get(
    "/prueba-auth",
    openapi_extra={"security": [{"Bearer": []}]}
)
async def prueba_autenticacion(current_user: UserORM = Security(get_current_user)):
    return {
        "mensaje": f"Autenticación exitosa para {current_user.email}",
        "user_id": str(current_user.id),
        "email": current_user.email,
        "roles": str([role.nombre for role in current_user.roles])
    }

# Endpoint para obtener la información del perfil de usuario
@router.get("/perfil", response_model=UserWithRoles, openapi_extra={"security": [{"Bearer": []}]})
async def obtener_perfil(
    current_user: UserORM = Security(get_current_user)
):
    """
    Obtener perfil del usuario autenticado
    """
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
    
    # Extraer roles para incluir en el token
    roles = [role.nombre for role in usuario.roles]
    print(f"Generando token para usuario {usuario.id} ({usuario.email}) con roles: {roles}")
    
    access_token = crear_token_acceso(
        data={
            "sub": str(usuario.id),  # Asegurar que sub es string
            "email": usuario.email,
            "roles": roles
        },
        expires_delta=access_token_expires
    )
    
    # Mostrar información del token generado
    print(f"Token generado: {access_token[:20]}...")
    
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint para registrar empleados (solo administradores)
@router.post(
    "/empleados", 
    response_model=UserWithRoles, 
    status_code=status.HTTP_201_CREATED
)
async def registro_empleado(
    usuario: UserCreate,
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
@router.put(
    "/{usuario_id}/roles", 
    response_model=UserWithRoles
)
async def asignar_roles(
    usuario_id: int,
    roles_ids: List[int],
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

# Endpoint que muestra los roles del usuario sin restricciones 
@router.get(
    "/mis-roles",
    response_model=Dict[str, Any],
    openapi_extra={"security": [{"Bearer": []}]}
)
async def verificar_mis_roles(current_user: UserORM = Security(get_current_user)):
    roles = [role.nombre for role in current_user.roles]
    return {"roles": roles, "id": current_user.id, "email": current_user.email} 

# Endpoint para obtener las reservas del usuario autenticado
@router.get(
    "/mis-reservas",
    response_model=List[Dict[str, Any]],
    openapi_extra={"security": [{"Bearer": []}]}
)
async def obtener_mis_reservas(
    current_user: UserORM = Security(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener todas las reservas del usuario autenticado
    """
    # Consulta de reservas del usuario autenticado
    reservas = db.query(ReservaORM).filter(ReservaORM.usuario_id == current_user.id).all()
    
    if not reservas:
        return []
    
    resultado = []
    for r in reservas:
        # Calcular noches de estancia
        noches = (r.fecha_fin - r.fecha_inicio).days
        
        # Obtener detalles y pagos
        detalles = db.query(DetalleReservaORM).filter(DetalleReservaORM.reserva_id == r.id).all()
        pagos = db.query(PagoORM).filter(PagoORM.reserva_id == r.id).all()
        
        # Calcular totales
        subtotal = sum(d.precio_por_noche * noches for d in detalles)
        impuestos = subtotal * 0.21  # 21% IVA
        total = subtotal + impuestos
        
        # Calcular pagado
        pagado = sum(p.monto for p in pagos)
        pendiente = total - pagado
        
        # Obtener habitaciones
        habitaciones = []
        for d in detalles:
            hab = db.query(HabitacionORM).filter(HabitacionORM.id == d.habitacion_id).first()
            if hab:
                habitaciones.append(hab.numero)
        
        # Crear objeto de reserva para la respuesta
        reserva_data = {
            "id": r.id,
            "codigo_reserva": r.codigo_reserva,
            "fecha_inicio": r.fecha_inicio,
            "fecha_fin": r.fecha_fin,
            "estado": r.estado,
            "numero_huespedes": r.numero_huespedes,
            "noches": noches,
            "habitaciones": habitaciones,
            "subtotal": subtotal,
            "impuestos": impuestos,
            "total": total,
            "pagado": pagado,
            "pendiente": pendiente,
            "fecha_creacion": r.fecha_creacion
        }
        
        resultado.append(reserva_data)
    
    return resultado 
