# Hoteleriapp API

API backend para la aplicación de gestión hotelera desarrollada con FastAPI.

## Requisitos

- Python 3.8+
- pip

## Instalación

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd Hoteleriapp
```

2. Crear un entorno virtual:
```bash
python -m venv venv
```

3. Activar el entorno virtual:

En Windows:
```bash
.\venv\Scripts\activate
```

En macOS/Linux:
```bash
source venv/bin/activate
```

4. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

## Ejecución

Para iniciar el servidor de desarrollo:

```bash
uvicorn main:app --reload
```

El servidor estará disponible en [http://localhost:8000](http://localhost:8000)

La documentación interactiva de la API estará disponible en:
- [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)
- [http://localhost:8000/redoc](http://localhost:8000/redoc) (ReDoc)

## Endpoints

### Generales
- `GET /`: Bienvenida a la API
- `GET /health`: Verificación del estado de la API

### Hoteles
- `GET /api/hotels`: Obtiene la lista de todos los hoteles
- `GET /api/hotels/{hotel_id}`: Obtiene un hotel por su ID
- `POST /api/hotels`: Crea un nuevo hotel
- `PUT /api/hotels/{hotel_id}`: Actualiza un hotel existente
- `DELETE /api/hotels/{hotel_id}`: Elimina un hotel 