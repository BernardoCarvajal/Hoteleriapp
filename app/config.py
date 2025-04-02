import os

# Configuración de JWT
SECRET_KEY = os.getenv("SECRET_KEY", "clave_super_secreta_para_desarrollo")
ALGORITHM = "HS256"

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hoteleriapp.db")

# Configuración de la aplicación
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "t") 