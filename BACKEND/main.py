import os
import uvicorn
from dotenv import load_dotenv
from app.init_db import init_db
from fastapi import FastAPI

# Importa todos los routers
from app.routers import usuarios, reservas, reportes, configuracion

# Carga las variables de entorno
load_dotenv()

# Inicializa la base de datos
init_db()

app = FastAPI()

# Incluye todos los routers
app.include_router(usuarios.router, prefix="/api/usuarios", tags=["usuarios"])
app.include_router(reservas.router, prefix="/api/reservas", tags=["reservas"])
app.include_router(reportes.router, prefix="/api/reportes", tags=["reportes"])
app.include_router(configuracion.router, prefix="/api/configuracion", tags=["configuracion"])

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "True").lower() == "true"
    
    uvicorn.run("main:app", host=host, port=port, reload=reload) 