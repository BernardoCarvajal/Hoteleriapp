from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.reservas import router as reservas_router
from app.routers.usuarios import router as usuarios_router
from app.routers.reportes import router as reportes_router
from app.routers.configuracion import router as configuracion_router

def create_app() -> FastAPI:
    """
    Crea y configura la aplicación FastAPI
    """
    app = FastAPI(
        title="Hoteleriapp API",
        description="API para la aplicación de gestión hotelera",
        version="0.1.0",
    )

    # Configuración de CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # En producción, especifica los orígenes permitidos
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root():
        return {"message": "¡Bienvenido a la API de Hoteleriapp!"}

    @app.get("/health")
    async def health_check():
        return {"status": "ok"}
    
    # Registramos los routers de la aplicación
    app.include_router(reservas_router, prefix="/api/reservas", tags=["reservas"])
    app.include_router(usuarios_router, prefix="/api/usuarios", tags=["usuarios"])
    app.include_router(reportes_router, prefix="/api/reportes", tags=["reportes"])
    app.include_router(configuracion_router, prefix="/api/configuracion", tags=["configuracion"])
    
    return app 