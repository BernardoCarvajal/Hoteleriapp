from fastapi import APIRouter, HTTPException, status, Depends, Security
from typing import List
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import Role
from app.models.user_orm import RoleORM
from app.routers.usuarios import get_admin_user

router = APIRouter()

# Endpoint para obtener todos los roles
@router.get("", response_model=List[Role])
async def obtener_roles(
    db: Session = Depends(get_db)
):
    """
    Obtener todos los roles disponibles
    """
    roles = db.query(RoleORM).all()
    return roles

# Endpoint para obtener un rol por ID
@router.get("/{rol_id}", response_model=Role)
async def obtener_rol(
    rol_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener un rol por ID
    """
    rol = db.query(RoleORM).filter(RoleORM.id == rol_id).first()
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rol con ID {rol_id} no encontrado"
        )
    return rol 