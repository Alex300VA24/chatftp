from flask import Flask, jsonify
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "base_datos", "usuarios.db")

app = Flask(__name__)

def obtener_usuarios_activos():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM usuarios WHERE activo = 1")
    usuarios = [fila[0] for fila in cursor.fetchall()]
    conn.close()
    return usuarios

@app.route("/usuarios-activos", methods=["GET"])
def usuarios_activos():
    return jsonify(obtener_usuarios_activos())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # Escucha desde fuera
