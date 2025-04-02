from fastapi import APIRouter, HTTPException, status, Depends, Cookie, Response, Header
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

from app.database import get_db
from app.models.configuracion import Configuracion, ConfiguracionUpdate, Idioma, CambioIdioma, CodigoIdioma
from app.models.configuracion_orm import ConfiguracionORM, IdiomaORM
from app.routers.usuarios import get_current_user, get_admin_user
from app.models.user_orm import UserORM

router = APIRouter()

# Endpoint para cambiar el idioma
@router.put(
    "/idioma", 
    response_model=Dict[str, str]
)
async def cambiar_idioma(
    idioma: CambioIdioma,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Cambiar el idioma de la aplicación
    """
    # Verificar que el idioma existe y está activo
    idioma_obj = db.query(IdiomaORM).filter(
        IdiomaORM.codigo == idioma.codigo,
        IdiomaORM.es_activo == True
    ).first()
    
    if not idioma_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Idioma con código {idioma.codigo} no encontrado o no está activo"
        )
    
    # Guardar preferencia en cookie
    response.set_cookie(
        key="idioma",
        value=idioma.codigo,
        max_age=60 * 60 * 24 * 30,  # 30 días
        httponly=True
    )
    
    # Si el usuario está autenticado, guardar preferencia en su perfil
    # Esto se implementaría si tuviéramos un campo para el idioma en el modelo de usuario
    
    return {"mensaje": f"Idioma cambiado a {idioma_obj.nombre}", "codigo": idioma.codigo}

# Endpoint para obtener idiomas disponibles
@router.get("/idiomas", response_model=List[Idioma])
async def obtener_idiomas(
    db: Session = Depends(get_db)
):
    """
    Obtener lista de idiomas disponibles
    """
    idiomas = db.query(IdiomaORM).filter(IdiomaORM.es_activo == True).all()
    return idiomas

# Endpoint para obtener idioma actual
@router.get("/idioma", response_model=Dict[str, str])
async def obtener_idioma_actual(
    idioma: Optional[str] = Cookie(None, alias="idioma"),
    db: Session = Depends(get_db)
):
    """
    Obtener el idioma actual del usuario
    """
    # Si no hay cookie de idioma, usar el idioma por defecto
    if not idioma:
        idioma_default = db.query(IdiomaORM).filter(IdiomaORM.es_default == True).first()
        if idioma_default:
            return {"codigo": idioma_default.codigo, "nombre": idioma_default.nombre}
        else:
            return {"codigo": "es", "nombre": "Español"}  # Valor predeterminado
    
    # Verificar que el idioma existe
    idioma_obj = db.query(IdiomaORM).filter(IdiomaORM.codigo == idioma).first()
    if idioma_obj:
        return {"codigo": idioma_obj.codigo, "nombre": idioma_obj.nombre}
    else:
        # Si el idioma de la cookie no existe, usar el idioma por defecto
        idioma_default = db.query(IdiomaORM).filter(IdiomaORM.es_default == True).first()
        if idioma_default:
            return {"codigo": idioma_default.codigo, "nombre": idioma_default.nombre}
        else:
            return {"codigo": "es", "nombre": "Español"}  # Valor predeterminado 