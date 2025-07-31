import sqlite3
import os

# Construye la ruta relativa al archivo actual
DB_PATH = os.path.join(os.path.dirname(__file__), "../base_datos/usuarios.db")
# Normaliza la ruta (opcional, pero útil)
DB_PATH = os.path.normpath(DB_PATH)

def obtener_usuarios():
    pass
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM usuarios")
        usuarios = cursor.fetchall()
        conn.close()
        return [u[0] for u in usuarios]
    except sqlite3.Error as e:
        print(f"Error al acceder a la base de datos: {e}")
        return []