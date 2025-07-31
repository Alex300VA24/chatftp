# servidor/utils.py
import os
from db import obtener_usuarios

# Diccionario global
directorios_actuales = {}

def inicializar_directorios():
    usuarios = obtener_usuarios()
    os.makedirs("usuarios", exist_ok=True)

    if not usuarios:
        print("⚠️ No hay usuarios registrados. No se crearán directorios.")
        return

    errores = []

    for username in usuarios:
        ruta = os.path.join("usuarios", username)
        try:
            os.makedirs(ruta, exist_ok=True)
            if not os.path.isdir(ruta):
                raise OSError(f"No se pudo verificar el directorio: {ruta}")
            directorios_actuales[username] = ruta
        except Exception as e:
            errores.append(f"Error con '{username}': {e}")

    if errores:
        print("❌ Se encontraron errores al crear directorios:")
        for err in errores:
            print("  -", err)
    else:
        print(f"✅ Directorios creados para {len(usuarios)} usuario(s): ")
