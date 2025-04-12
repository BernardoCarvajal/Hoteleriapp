from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from app.routers.reservas import router as reservas_router
from app.routers.usuarios import router as usuarios_router
from app.routers.reportes import router as reportes_router
from app.routers.configuracion import router as configuracion_router

# Importar los modelos Pydantic para incluirlos en el esquema OpenAPI
from app.models.user import User, UserCreate, UserLogin, UserWithRoles, Token
from app.models.schemas.http_error import HTTPValidationError, ValidationError

security_scheme = HTTPBearer()

def create_app() -> FastAPI:
    """
    Crea y configura la aplicación FastAPI
    """
    app = FastAPI(
        title="Hoteleriapp API",
        description="API para la aplicación de gestión hotelera",
        version="0.1.0",
    )

    # Configuración de CORS más permisiva
    origins = [
        "http://localhost",
        "http://localhost:8000",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        "https://hoteleriapp-1.onrender.com",
        # Añade aquí otros orígenes que necesites permitir
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,  # Lista de orígenes permitidos
        allow_credentials=True,  # Permite enviar cookies en solicitudes CORS
        allow_methods=["*"],    # Permite todos los métodos HTTP
        allow_headers=["*"],    # Permite todos los headers
        expose_headers=["*"],   # Expone todos los headers
        max_age=600,            # Tiempo máximo de caché para preflight requests (10 minutos)
    )

    # Configurar el esquema de seguridad para Swagger UI
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        
        # Agregar componentes de seguridad JWT
        if "components" not in openapi_schema:
            openapi_schema["components"] = {}
            
        openapi_schema["components"]["securitySchemes"] = {
            "Bearer": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Ingresa tu token JWT con el formato: **Bearer eyJhbGc...**"
            }
        }
        
        # Aplicar seguridad global a todas las rutas
        openapi_schema["security"] = [{"Bearer": []}]
        
        # Aplicar seguridad a nivel de ruta para todos los endpoints que necesitan autenticación
        for path in openapi_schema["paths"].values():
            for operation in path.values():
                # Asegurarnos de que todos los endpoints tienen definida la seguridad
                if "security" not in operation:
                    operation["security"] = [{"Bearer": []}]
        
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    
    app.openapi = custom_openapi

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