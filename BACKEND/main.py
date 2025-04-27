import os
import uvicorn
from dotenv import load_dotenv
from app.api import create_app
from app.init_db import init_db
from fastapi import FastAPI
from app.routers import usuarios

# Carga las variables de entorno
load_dotenv()

# Inicializa la base de datos
init_db()

app = FastAPI()

app.include_router(usuarios.router, prefix="/api/usuarios", tags=["usuarios"])

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "True").lower() == "true"
    
    uvicorn.run("main:app", host=host, port=port, reload=reload) 