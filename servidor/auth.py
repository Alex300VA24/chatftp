
import sqlite3
import os

# Ruta más robusta
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "base_datos", "usuarios.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)  # Crea directorios necesarios

def inicializar_bd():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            activo INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def activar_usuario(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE usuarios SET activo = 1 WHERE username = ?", (username,))
    conn.commit()
    conn.close()

def desactivar_usuario(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE usuarios SET activo = 0 WHERE username = ?", (username,))
    conn.commit()
    conn.close()



def registrar_usuario(username, password):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return "REGISTER_OK"
    except sqlite3.IntegrityError:
        return "REGISTER_ERROR: Usuario ya existe"
    finally:
        conn.close()

def verificar_credenciales(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (username, password))
    resultado = cursor.fetchone()
    conn.close()
    if resultado:
        return "LOGIN_OK"
    else:
        return "LOGIN_ERROR: Usuario o contraseña incorrectos"

