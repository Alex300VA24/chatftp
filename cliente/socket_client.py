import os
import socket
import threading
import base64

ruta_actual = []  # mantiene seguimiento de las rutas locales del usuario


SERVER_IP = "192.168.3.38"
#SERVER_IP = "172.30.17.209"
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
    if f not in listeners:
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

def subir_archivo(username, path_local):
    with open(path_local, "rb") as f:
        data = f.read()

    nombre = os.path.basename(path_local)
    bloques = [data[i:i+1024] for i in range(0, len(data), 1024)]

    enviar_mensaje(f"PUT_START|{username}|{nombre}|{len(bloques)}")
    for i, bloque in enumerate(bloques):
        data_b64 = base64.b64encode(bloque).decode()
        enviar_mensaje(f"PUT_BLOCK|{username}|{nombre}|{i}|{data_b64}")
    return enviar_mensaje(f"PUT_END|{username}|{nombre}")

def descargar_archivo(username, nombre, destino):
    print(f"Iniciando descarga de {nombre} para {username}")
    bloques = {}
    total_bloques = None

    # Paso 1: Iniciar GET
    respuesta = enviar_mensaje(f"GET_START|{username}|{nombre}")
    if not respuesta or not respuesta.startswith("GET_READY"):
        raise Exception("Error al iniciar la descarga")

    _, archivo, total_str = respuesta.split("|")
    total_bloques = int(total_str)
    print(f"Total bloques esperados: {total_bloques}")

    # Paso 2: Solicitar cada bloque uno por uno
    for i in range(total_bloques):
        intentos = 0
        bloque_recibido = False
        while intentos < 5 and not bloque_recibido:
            respuesta = enviar_mensaje(f"GET_ACK|{username}|{nombre}|{i}")
            if respuesta and respuesta.startswith("GET_BLOCK|"):
                try:
                    _, nombre_archivo, bloque_id_str, data_b64 = respuesta.split("|", 3)
                    bloque_id = int(bloque_id_str)
                    if bloque_id == i:
                        bloques[bloque_id] = base64.b64decode(data_b64)
                        print(f"Recibido bloque {bloque_id}")
                        bloque_recibido = True
                    else:
                        print(f"[INTENTO {intentos+1}] Bloque no coincide → {respuesta[:50]}...")
                except Exception as ex:
                    print(f"[INTENTO {intentos+1}] Error al procesar el bloque: {ex}")
            else:
                print(f"[INTENTO {intentos+1}] Timeout o respuesta inválida para bloque {i}")
            intentos += 1

        if not bloque_recibido:
            raise Exception(f"Timeout al recibir el bloque {i}: ERROR|Timeout: No se obtuvo respuesta validad del servidor")

    # Paso 3: Esperar GET_END
    try:
        data, _ = sock.recvfrom(BUFFER_SIZE)
        mensaje = data.decode()
        if mensaje.startswith("GET_END"):
            print("Transferencia finalizada correctamente.")
        else:
            print("Advertencia: No se recibió GET_END explícitamente.")
    except socket.timeout:
        print("Timeout esperando GET_END. Continuando...")

    # Paso 4: Guardar archivo
    with open(destino, "wb") as f:
        for i in range(total_bloques):
            f.write(bloques.get(i, b""))  # Manejo de posibles huecos (aunque ya controlamos)
    print(f"Archivo guardado en {destino}")


def limpiar_mensaje_respuesta(respuesta):
    if respuesta.startswith("SEQ_ACK="):
        partes = respuesta.split("|", 1)
        if len(partes) == 2:
            return partes[1]
    return respuesta

def descargar_archivo_de_otro_usuario(usuario_origen, nombre_archivo, ruta_relativa_en_origen, destino_local):
    print(f"Iniciando descarga de {nombre_archivo} desde {usuario_origen}:{ruta_relativa_en_origen}")
    bloques = {}

    # 1. Iniciar descarga: solicitar metadatos del archivo
    respuesta = enviar_mensaje(f"GET_START_FROM|{usuario_origen}|{ruta_relativa_en_origen}|{nombre_archivo}")
    respuesta = limpiar_mensaje_respuesta(respuesta)

    if not respuesta or not respuesta.startswith("GET_READY_CHAT"):
        raise Exception(f"Error al iniciar descarga: {respuesta}")

    _, archivo, total_str = respuesta.split("|")
    total_bloques = int(total_str)
    print(f"Total bloques esperados: {total_bloques}")

    # 2. Solicitar cada bloque
    for i in range(total_bloques):
        intentos = 0
        bloque_recibido = False

        while intentos < 5 and not bloque_recibido:
            respuesta = enviar_mensaje(
                f"GET_ACK_FROM|{usuario_origen}|{ruta_relativa_en_origen}|{nombre_archivo}|{i}"
            )
            respuesta = limpiar_mensaje_respuesta(respuesta)

            if respuesta and respuesta.startswith("GET_BLOCK"):
                try:
                    _, nombre_archivo_r, bloque_id_str, data_b64 = respuesta.split("|", 3)
                    bloque_id = int(bloque_id_str)

                    if bloque_id == i:
                        bloques[bloque_id] = base64.b64decode(data_b64)
                        print(f"✅ Recibido bloque {bloque_id}")
                        bloque_recibido = True
                except Exception as ex:
                    print(f"[INTENTO {intentos+1}] Error procesando bloque {i}: {ex}")
            else:
                print(f"[INTENTO {intentos+1}] Respuesta inválida o timeout")

            intentos += 1

        if not bloque_recibido:
            raise Exception(f"❌ Timeout al recibir el bloque {i}")

    # 3. Esperar GET_END_CHAT (opcional)
    try:
        data, _ = sock.recvfrom(BUFFER_SIZE)
        mensaje = data.decode()
        mensaje = limpiar_mensaje_respuesta(mensaje)
        if not mensaje.startswith("GET_END_CHAT"):
            print("⚠️ Advertencia: No se recibió GET_END_CHAT")
    except socket.timeout:
        print("⚠️ Timeout esperando GET_END_CHAT")

    # 4. Guardar archivo
    with open(destino_local, "wb") as f:
        for i in range(total_bloques):
            f.write(bloques.get(i, b""))

    print(f"📁 Archivo guardado en {destino_local}")



def procesar_notify(mensaje: str, username: str) -> str | None:
    try:
        print('Llega a procesar notify')
        partes = mensaje.split("|")
        if len(partes) == 2:
            _, remitente = partes  # "NOTIFY", "Julio"
            if remitente != username:  # Si el remitente NO soy yo
                return remitente  # entonces muestro notificación
    except Exception as ex:
        print(f"[ERROR NOTIFY] {ex}")
    return None




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

