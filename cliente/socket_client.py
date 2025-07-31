import os
import socket
import threading

ruta_actual = []  # mantiene seguimiento de las rutas locales del usuario


SERVER_IP = "192.168.3.38"
#SERVER_IP = "172.30.12.61"
SERVER_PORT = 2121
BUFFER_SIZE = 4096
REINTENTOS = 5

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(5)

listeners = []

seq_actual = 0  # Contador global

def enviar_mensaje(mensaje: str) -> str:
    global seq_actual

    intentos = 0
    while intentos < REINTENTOS:
        seq_str = f"SEQ={seq_actual}"
        mensaje_completo = f"{seq_str}|{mensaje}"

        try:
            sock.sendto(mensaje_completo.encode(), (SERVER_IP, SERVER_PORT))
            respuesta, _ = sock.recvfrom(BUFFER_SIZE)
            respuesta_str = respuesta.decode()

            if respuesta_str.startswith(f"SEQ_ACK={seq_actual}|"):
                # ✅ Coincide el ACK, extraer la parte útil
                parte_util = respuesta_str.split("|", 1)[1]
                seq_actual += 1  # Incrementa solo si se confirmó
                return parte_util
            else:
                print(f"[INTENTO {intentos + 1}] SEQ no coincide o respuesta inválida → {respuesta_str}")

        except socket.timeout:
            print(f"[INTENTO {intentos + 1}] Timeout al enviar: {mensaje_completo}")

        intentos += 1

    return "ERROR|Timeout: No se obtuvo respuesta válida del servidor"



def iniciar_escucha(f):
    listeners.append(f)

def loop_escucha():
    while True:
        try:
            data, _ = sock.recvfrom(BUFFER_SIZE)
            mensaje = data.decode()
            for f in listeners:
                f(mensaje)
        except:
            pass

def listar_directorio(username):
    respuesta = enviar_mensaje(f"LS|{username}")
    print(f"[DEBUG raw LS] => {respuesta}")  # 👈 importante

    if respuesta.startswith("LS|"):
        partes = respuesta.split("|")
        archivos = partes[1:]

        archivos_filtrados = [a for a in archivos if a.strip()]

        # Si estamos en raíz, nunca mostrar ".."
        if ruta_actual == []:
            archivos_filtrados = [a for a in archivos_filtrados if a != ".."]

        if ruta_actual and ".." not in archivos_filtrados:
            archivos_filtrados.insert(0, "..")

        print(f"[{username}] Contenido del directorio actual:")
        for archivo in archivos_filtrados:
            print(f" - {archivo}")

        return archivos_filtrados
    else:
        # Aquí detectamos si llegó un mensaje inesperado de CD o algún error
        if respuesta.startswith("CD_OK|"):
            print("[WARN] Recibida respuesta CD_OK en lugar de LS.")
            # Podrías intentar ignorar o sincronizar el estado, o forzar un reintento
            return []
        elif respuesta.startswith("ERROR|"):
            print(f"Error al listar: {respuesta}")
            return []
        else:
            print(f"Respuesta inesperada al listar: {respuesta}")
            return []

def crear_directorio(username, nombre):
    respuesta = enviar_mensaje(f"MKDIR|{username}|{nombre}")
    print("Intento crear:", nombre)
    print("Respuesta del servidor:", respuesta)

def eliminar_directorio(username, nombre):
    respuesta = enviar_mensaje(f"RMDIR|{username}|{nombre}")
    print("Respuesta del servidor:", respuesta)

def eliminar_archivo(username, nombre):
    respuesta = enviar_mensaje(f"RM|{username}|{nombre}")
    print("Respuesta del servidor:", respuesta)




# actualizar cambiar_directorio
def cambiar_directorio(username, subcarpeta):
    global ruta_actual
    print(f"[DEBUG subcarpeta] => {repr(subcarpeta)}")

    respuesta = enviar_mensaje(f"CD|{username}|{subcarpeta}")
    print(f"[DEBUG cambiar_directorio] Enviado: CD|{username}|{subcarpeta} → Respuesta: {respuesta}")

    if respuesta.startswith("CD_OK|"):
        if subcarpeta == "..":
            if ruta_actual:
                ruta_actual.pop()
        else:
            ruta_actual.append(subcarpeta)
        print(f"[DEBUG ruta_actual] => {ruta_actual}")
        return True
    else:
        print(f"[DEBUG cambiar_directorio] Falló CD → {respuesta}")
        return False







def obtener_ruta_actual():
    return "/" + "/".join(ruta_actual) if ruta_actual else "/"




# Hilo de escucha global
threading.Thread(target=loop_escucha, daemon=True).start()

