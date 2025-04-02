from app.database import engine, SessionLocal, Base
from app.models.user_orm import UserORM, RoleORM
from app.models.habitacion_orm import HabitacionORM, TipoHabitacionORM
from app.models.reserva_orm import ReservaORM, DetalleReservaORM, PagoORM, EstadoReserva, EstadoPago
from app.models.configuracion_orm import ConfiguracionORM, IdiomaORM
from app.models.reporte_orm import ReporteORM

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
import random
import string
from werkzeug.security import generate_password_hash

# Datos iniciales
def get_initial_data():
    # Roles
    roles_data = [
        {"nombre": "admin", "descripcion": "Administrador del sistema"},
        {"nombre": "empleado", "descripcion": "Empleado del hotel"},
        {"nombre": "cliente", "descripcion": "Cliente registrado"}
    ]
    
    # Usuarios
    usuarios_data = [
        {
            "nombre": "Admin",
            "apellido": "Sistema",
            "email": "admin@hoteleriapp.com",
            "password_hash": generate_password_hash("admin123"),
            "telefono": "123456789",
            "documento_identidad": "A12345678",
            "es_activo": True,
            "roles": ["admin"]
        },
        {
            "nombre": "Juan",
            "apellido": "Pérez",
            "email": "juan@ejemplo.com",
            "password_hash": generate_password_hash("password123"),
            "telefono": "987654321",
            "documento_identidad": "B87654321",
            "es_activo": True,
            "roles": ["cliente"]
        }
    ]
    
    # Tipos de habitaciones
    tipos_habitacion_data = [
        {
            "nombre": "Individual",
            "descripcion": "Habitación con una cama individual",
            "precio_base": 80.0,
            "capacidad": 1
        },
        {
            "nombre": "Doble",
            "descripcion": "Habitación con una cama doble o dos individuales",
            "precio_base": 120.0,
            "capacidad": 2
        },
        {
            "nombre": "Suite",
            "descripcion": "Suite de lujo con salón y dormitorio",
            "precio_base": 200.0,
            "capacidad": 2
        },
        {
            "nombre": "Familiar",
            "descripcion": "Habitación amplia para familias",
            "precio_base": 180.0,
            "capacidad": 4
        }
    ]
    
    # Habitaciones
    habitaciones_data = []
    for piso in range(1, 5):
        for numero in range(1, 8):
            tipo_id = random.randint(1, len(tipos_habitacion_data))
            habitaciones_data.append({
                "numero": f"{piso}0{numero}",
                "piso": piso,
                "tipo_id": tipo_id,
                "esta_activa": True,
                "notas": f"Habitación {piso}0{numero}"
            })

    # Idiomas
    idiomas_data = [
        {"codigo": "es", "nombre": "Español", "es_activo": True, "es_default": True},
        {"codigo": "en", "nombre": "English", "es_activo": True, "es_default": False}
    ]
    
    # Configuraciones
    configuraciones_data = [
        {"clave": "hotel_nombre", "valor": "Hoteleriapp", "descripcion": "Nombre del hotel"},
        {"clave": "moneda_default", "valor": "EUR", "descripcion": "Moneda por defecto"},
        {"clave": "checkin_hora", "valor": "14:00", "descripcion": "Hora de check-in"},
        {"clave": "checkout_hora", "valor": "12:00", "descripcion": "Hora de check-out"},
        {"clave": "iva_porcentaje", "valor": "21", "descripcion": "Porcentaje de IVA"}
    ]
    
    return {
        "roles": roles_data,
        "usuarios": usuarios_data,
        "tipos_habitacion": tipos_habitacion_data,
        "habitaciones": habitaciones_data,
        "idiomas": idiomas_data,
        "configuraciones": configuraciones_data
    }

def init_db():
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    # Crear sesión
    db = SessionLocal()
    
    try:
        initial_data = get_initial_data()
        
        # Insertar roles
        if db.query(RoleORM).count() == 0:
            for role_data in initial_data["roles"]:
                db_role = RoleORM(**role_data)
                db.add(db_role)
            db.commit()
            print("Roles inicializados")
        
        # Insertar usuarios
        if db.query(UserORM).count() == 0:
            roles = {role.nombre: role for role in db.query(RoleORM).all()}
            
            for user_data in initial_data["usuarios"]:
                user_roles = user_data.pop("roles", [])
                db_user = UserORM(**user_data)
                
                # Asignar roles
                for role_name in user_roles:
                    if role_name in roles:
                        db_user.roles.append(roles[role_name])
                
                db.add(db_user)
            db.commit()
            print("Usuarios inicializados")
        
        # Insertar tipos de habitaciones
        if db.query(TipoHabitacionORM).count() == 0:
            for tipo_data in initial_data["tipos_habitacion"]:
                db_tipo = TipoHabitacionORM(**tipo_data)
                db.add(db_tipo)
            db.commit()
            print("Tipos de habitaciones inicializados")
        
        # Insertar habitaciones
        if db.query(HabitacionORM).count() == 0:
            for habitacion_data in initial_data["habitaciones"]:
                db_habitacion = HabitacionORM(**habitacion_data)
                db.add(db_habitacion)
            db.commit()
            print("Habitaciones inicializadas")
        
        # Insertar idiomas
        if db.query(IdiomaORM).count() == 0:
            for idioma_data in initial_data["idiomas"]:
                db_idioma = IdiomaORM(**idioma_data)
                db.add(db_idioma)
            db.commit()
            print("Idiomas inicializados")
        
        # Insertar configuraciones
        if db.query(ConfiguracionORM).count() == 0:
            for config_data in initial_data["configuraciones"]:
                db_config = ConfiguracionORM(**config_data)
                db.add(db_config)
            db.commit()
            print("Configuraciones inicializadas")
        
        print("Base de datos inicializada correctamente")
    
    except IntegrityError as e:
        print(f"Error de integridad al inicializar la base de datos: {e}")
        db.rollback()
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db() 