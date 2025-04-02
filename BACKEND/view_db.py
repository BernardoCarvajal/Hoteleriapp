import sqlite3
import os

def view_db():
    # Verificar si el archivo de la base de datos existe
    if not os.path.exists("hoteleriapp.db"):
        print("La base de datos no existe. Ejecuta la aplicación primero para crearla.")
        return
    
    # Conectar a la base de datos
    conn = sqlite3.connect("hoteleriapp.db")
    cursor = conn.cursor()
    
    # Listar todas las tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    if not tables:
        print("No hay tablas en la base de datos.")
        conn.close()
        return
    
    print("Tablas en la base de datos:")
    for table in tables:
        table_name = table[0]
        print(f"\n[Tabla: {table_name}]")
        
        # Obtener la estructura de la tabla
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        print("\nEstructura:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Obtener los datos de la tabla
        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()
        print(f"\nDatos ({len(rows)} registros):")
        
        if rows:
            col_names = [col[1] for col in columns]
            for i, row in enumerate(rows):
                print(f"\nRegistro #{i+1}:")
                for j, value in enumerate(row):
                    print(f"  {col_names[j]}: {value}")
    
    # Cerrar la conexión
    conn.close()

if __name__ == "__main__":
    view_db() 