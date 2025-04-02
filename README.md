# Hoteleriapp API

API backend para el sistema de gestión hotelera desarrollado con FastAPI y SQLite.

## Descripción

Hoteleriapp es una aplicación de gestión hotelera que permite administrar reservas, usuarios, habitaciones y generar reportes. Este proyecto implementa el backend utilizando FastAPI, SQLAlchemy y SQLite como base de datos.

## Requisitos

- Python 3.8+ (recomendado Python 3.13)
- pip

## Estructura del Proyecto

```
Hoteleriapp/
├── app/                # Directorio principal de la aplicación
│   ├── models/         # Modelos Pydantic y ORM
│   ├── routers/        # Routers para los endpoints 
│   ├── services/       # Servicios y lógica de negocio
│   ├── api.py          # Configuración de la API
│   ├── database.py     # Configuración de la base de datos
│   └── init_db.py      # Inicialización de la base de datos
├── .env                # Variables de entorno
├── .env.example        # Ejemplo de variables de entorno
├── main.py             # Punto de entrada de la aplicación
├── requirements.txt    # Dependencias del proyecto
└── README.md           # Este archivo
```

## Instalación

1. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## Configuración

2. Crea un archivo `.env` basado en `.env.example`:
```bash
copy .env.example .env  # En Windows
# o
cp .env.example .env    # En Unix/Linux/MacOS
```

3. Edita el archivo `.env` con la configuración deseada.

## Ejecución

Para ejecutar la aplicación, usa el siguiente comando:

```bash
python -3.13 main.py
# o simplemente 
python main.py  # Si Python 3.13 es tu versión por defecto
```

La aplicación estará disponible en:
- http://localhost:8000 - Endpoint principal
- http://localhost:8000/docs - Documentación interactiva (Swagger UI)

## Endpoints Disponibles

### Gestión de Reservas
- `GET /api/reservas/disponibilidad` - Consultar disponibilidad de habitaciones
- `POST /api/reservas` - Registrar una reserva
- `POST /api/reservas/costo` - Calcular el costo de la reserva
- `POST /api/pagos` - Realizar el pago de una reserva
- `GET /api/reservas/{id}/ticket` - Generar ticket de check-in con código QR

### Gestión de Usuarios
- `POST /api/usuarios/registro` - Registro de clientes
- `POST /api/usuarios/login` - Login de usuarios con JWT
- `POST /api/usuarios/empleados` - Registrar empleados (solo administradores)
- `PUT /api/usuarios/{id}/roles` - Asignación de roles

### Reportes
- `GET /api/reportes/reservas` - Generar reportes de reservas
- `GET /api/reportes/ocupacion` - Obtener ocupación en tiempo real

### Configuraciones
- `PUT /api/configuracion/idioma` - Cambio de idioma (es/en)
- `GET /api/configuracion/idiomas` - Listar idiomas disponibles
- `GET /api/configuracion/idioma` - Obtener idioma actual

## Base de Datos

El proyecto utiliza SQLite como base de datos. El archivo de la base de datos (`hoteleriapp.db`) se crea automáticamente en la carpeta raíz al ejecutar la aplicación.

Para ver el contenido de la base de datos, puedes utilizar:

1. El script incluido:
```bash
python view_db.py
```

2. Herramientas externas como:
   - [SQLiteStudio](https://sqlitestudio.pl/)
   - Con SQLITESTUDIO seleccionan hoteleriapp.db y podrán ver toda la bbdd (Acuérdense que antes tiene que estar inicializado el swagger)

## Usuarios Predefinidos

Para facilitar las pruebas, la aplicación incluye dos usuarios predefinidos:

1. **Administrador**:
   - Email: admin@hoteleriapp.com
   - Contraseña: admin123

2. **Cliente**:
   - Email: juan@ejemplo.com
   - Contraseña: password123

## Solución de Problemas

### Error "No module named 'uvicorn'"
Si recibes este error, asegúrate de que uvicorn está instalado correctamente:
```bash
pip install uvicorn
```

### Problemas con la instalación de Pillow
Si tienes problemas al instalar Pillow, puedes intentar:
```bash
pip install --only-binary=:all: Pillow
```