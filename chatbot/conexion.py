import sqlite3
import os

def execute_sql_file(db_name, sql_file):
    """Ejecuta un archivo SQL en la base de datos especificada."""
    if not os.path.exists(sql_file):
        print(f"Error: El archivo {sql_file} no existe.")
        return False
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    with open(sql_file, 'r', encoding='utf-8') as file:
        sql_script = file.read()
    
    # Dividir en sentencias individuales
    statements = sql_script.split(';')
    
    for statement in statements:
        statement = statement.strip()
        if statement:  # Evitar sentencias vacías
            try:
                cursor.execute(statement)
                print(f"✅ Ejecutado: {statement[:50]}...")
            except sqlite3.Error as e:
                print(f"❌ Error en: {statement[:50]}...")
                print(f"   Detalle: {e}")
                conn.close()
                return False
    
    conn.commit()
    conn.close()
    return True

def setup_database():
    """Configura la base de datos ejecutando el archivo SQL."""
    db_name = "base.db"
    sql_file = "sentencias.sql"  # Cambiado a "sentencias.sql"
    
    if execute_sql_file(db_name, sql_file):
        print("\n🎉 Base de datos configurada exitosamente!")
        return True
    else:
        print("\n❌ Error al configurar la base de datos.")
        return False

if __name__ == "__main__":
    setup_database()