# Explicación Detallada del Proyecto Hoteleriapp

## Visión General

Hoteleriapp es un sistema de gestión hotelera que permite administrar reservas, usuarios y generar reportes. El proyecto está construido con tecnologías modernas como:

- **FastAPI**: Framework de Python para crear APIs web rápidas
- **SQLite**: Base de datos ligera que guarda toda la información en un archivo
- **SQLAlchemy**: Herramienta que conecta Python con la base de datos
- **JWT**: Sistema de tokens para autenticación de usuarios

## Estructura del Proyecto Explicada

### Carpetas Principales

#### 📁 app/
Es el corazón del proyecto donde está todo el código.

- **models/**: Contiene dos tipos de archivos:
  - Archivos `*_orm.py`: Definen cómo se guarda la información en la base de datos
  - Archivos `*.py`: Definen la estructura de los datos que se envían/reciben en la API

- **routers/**: Cada archivo controla un grupo de funcionalidades:
  - `usuarios.py`: Todo lo relacionado con login, registro y permisos
  - `reservas.py`: Maneja las reservas, disponibilidad y pagos
  - `reportes.py`: Genera informes de ocupación y estadísticas
  - `configuracion.py`: Controla configuraciones como el idioma

- **api.py**: Archivo central que conecta todos los routers y configura la API

- **database.py**: Establece la conexión con la base de datos SQLite

- **init_db.py**: Crea las tablas en la base de datos e inserta datos iniciales (usuarios predefinidos)

### Archivos en la Raíz

- **main.py**: El punto de entrada que inicia toda la aplicación
- **requirements.txt**: Lista de bibliotecas necesarias para que funcione el proyecto
- **.env**: Archivo con configuraciones sensibles (contraseñas, claves secretas)
- **hoteleriapp.db**: Base de datos SQLite que se crea automáticamente

## Cómo Funciona el Sistema

### 1. Inicio de la Aplicación

Cuando ejecutas `py -3.13 main.py` o `py -3.13 -m uvicorn main:app --reload`, ocurre lo siguiente:

1. El archivo `main.py` importa la configuración desde `app/api.py`
2. Se ejecuta `init_db.py` para crear o actualizar la base de datos
3. El servidor web se inicia y comienza a escuchar en http://localhost:8000

### 2. Autenticación de Usuarios

El sistema usa tokens JWT (como llaves digitales temporales):

1. El usuario envía su email y contraseña a `/api/usuarios/login`
2. Si son correctos, recibe un token que dura 30 minutos
3. Este token debe incluirse en todas las peticiones siguientes

### 3. Flujo de una Reserva

Cuando alguien hace una reserva:

1. Primero consulta disponibilidad con `/api/reservas/disponibilidad`
2. Calcula el costo usando `/api/reservas/costo`
3. Crea la reserva con `/api/reservas`
4. Realiza el pago mediante `/api/pagos`
5. Obtiene un ticket con código QR usando `/api/reservas/{id}/ticket`

### 4. Base de Datos

Toda la información se guarda en un archivo SQLite (`hoteleriapp.db`):

- **Usuarios**: Almacena clientes, empleados y administradores
- **Roles**: Define los permisos de cada usuario
- **Reservas**: Guarda la información de cada reserva
- **Habitaciones**: Contiene los tipos y características
- **Pagos**: Registra los pagos de las reservas

## Conexiones Entre Componentes

1. **Frontend ↔️ API**: Cualquier aplicación cliente se conecta mediante peticiones HTTP a los endpoints
2. **API ↔️ Routers**: La API recibe peticiones y las dirige al router correspondiente
3. **Routers ↔️ Modelos**: Los routers usan modelos para validar la información recibida
4. **Modelos ↔️ Base de datos**: Los modelos ORM permiten guardar y recuperar información

## Cómo Probar el Sistema

1. Inicia el servidor con `py -3.13 main.py`
2. Abre http://localhost:8000/docs para ver la documentación interactiva (Swagger UI)
3. Prueba el login con el usuario administrador: 
   - Email: admin@hoteleriapp.com
   - Contraseña: admin123
4. Haz clic en "Authorize" e ingresa el token recibido
5. Ahora puedes probar cualquier endpoint desde la interfaz

## Diagnóstico de Problemas Comunes

### Si la aplicación no inicia:
- Verifica que todas las dependencias estén instaladas con `pip install -r requirements.txt`
- Asegúrate de tener Python 3.8 o superior

### Si hay errores de CORS:
- Asegúrate de que las peticiones vengan de un origen permitido (como http://localhost:3000)
- Usa el protocolo `http://` y no `file://`

### Si las peticiones fallan con error 401 o 422:
- El token podría haber expirado (dura 30 minutos)
- Verifica que el formato sea: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

Este sistema está diseñado para ser escalable y mantener una clara separación de responsabilidades, lo que facilita su mantenimiento y extensión con nuevas funcionalidades.