import sqlite3
import os

# Configuración de la base de datos
DB_NAME = "base.db"
SQL_FILE = "sentencias.sql"

def setup_database():
    # Verificar si el archivo SQL existe
    if not os.path.exists(SQL_FILE):
        print(f"Error: El archivo {SQL_FILE} no existe.")
        return
    
    # Conectar a la base de datos
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Leer el archivo SQL
    with open(SQL_FILE, 'r', encoding='utf-8') as file:
        sql_script = file.read()
    
    # Dividir en sentencias individuales
    statements = sql_script.split(';')
    
    # Ejecutar cada sentencia
    for statement in statements:
        statement = statement.strip()
        if statement:  # Evitar sentencias vacías
            try:
                cursor.execute(statement)
                print(f"Ejecutado: {statement[:50]}...")
            except sqlite3.Error as e:
                print(f"Error en: {statement[:50]}...")
                print(f"   Detalle: {e}")
    
    # Guardar cambios y cerrar conexión
    conn.commit()
    conn.close()
    print("\nBase de datos configurada exitosamente!")
    
    # Verificar tablas creadas
    print("\nTablas creadas:")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        print(f"- {table[0]}")
    conn.close()

if __name__ == "__main__":
    setup_database()