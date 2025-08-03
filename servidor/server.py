import socket
import threading
import math
import os
import time
import base64
from auth import inicializar_bd, registrar_usuario, verificar_credenciales, activar_usuario, desactivar_usuario
from utils import inicializar_directorios, directorios_actuales


SERVER_IP = "0.0.0.0"
SERVER_PORT = 2121
BUFFER_SIZE = 4096

clientes_conectados = {}  # usuario: (ip, port)
archivos_en_recepcion = {}

lock = threading.Lock()

# Diccionario para llevar el directorio actual de cada usuario
directorios_actuales = {}
cache_respuestas = {}
# Estado para envíos GET por cliente
archivos_en_envio = {}



def manejar_mensaje(data, addr, sock):
    mensaje_completo = data.decode()
    if not mensaje_completo.startswith("SEQ="):
        respuesta = "ERROR|Falta número de secuencia (SEQ)"
        sock.sendto(respuesta.encode(), addr)
        return

    # Extrae SEQ
    try:
        encabezado, mensaje = mensaje_completo.split("|", 1)
        seq = int(encabezado.split("=")[1])
    except:
        respuesta = "ERROR|Formato inválido de SEQ"
        respuesta_final = f"SEQ_ACK={seq}|{respuesta}"
        cache_respuestas[addr] = (seq, respuesta)
        sock.sendto(respuesta_final.encode(), addr)
        return

    # Revisa si ya se procesó este SEQ para este cliente
    ultimo_seq, ultima_respuesta = cache_respuestas.get(addr, (-1, None))
    if seq == ultimo_seq:
        # Reenviar sin reprocesar
        print(f"[REINTENTO DETECTADO] Reenviando respuesta caché a {addr} para SEQ={seq}")
        sock.sendto(f"SEQ_ACK={seq}|{ultima_respuesta}".encode(), addr)
        return


    print(f"[DEBUG] Mensaje recibido de {addr}: {mensaje}")

    if mensaje.startswith("REGISTER|"):
        partes = mensaje.split("|")
        comando = partes[0]
        username, password = partes[1], partes[2]
        respuesta = registrar_usuario(username, password)
        respuesta_final = f"SEQ_ACK={seq}|{respuesta}"
        cache_respuestas[addr] = (seq, respuesta)
        sock.sendto(respuesta_final.encode(), addr)


    elif mensaje.startswith("LOGIN|"):
        partes = mensaje.split("|")
        if len(partes) != 3:
            respuesta = "ERROR|Formato inválido de LOGIN"
            sock.sendto(f"SEQ_ACK={seq}|{respuesta}".encode(), addr)
            return

        usuario, password = partes[1], partes[2]

        if verificar_credenciales(usuario, password):
            activar_usuario(usuario)
            with lock:
                clientes_conectados[usuario] = addr
            ruta_usuario = os.path.join("usuarios", usuario)
            if not os.path.exists(ruta_usuario):
                os.makedirs(ruta_usuario)
            directorios_actuales[usuario] = os.path.abspath(ruta_usuario)
            respuesta = "LOGIN_OK"
        else:
            respuesta = "ERROR|Credenciales inválidas"


        respuesta_final = f"SEQ_ACK={seq}|{respuesta}"
        cache_respuestas[addr] = (seq, respuesta)
        sock.sendto(respuesta_final.encode(), addr)

    
    elif mensaje.startswith("LOGOUT|"):
        partes = mensaje.split("|")
        if len(partes) != 2:
            respuesta = "ERROR|Formato inválido de LOGOUT"
            sock.sendto(f"SEQ_ACK={seq}|{respuesta}".encode(), addr)
            return

        usuario = partes[1]
        desactivar_usuario(usuario)
        with lock:
            if usuario in clientes_conectados:
                del clientes_conectados[usuario]
            if usuario in directorios_actuales:
                del directorios_actuales[usuario]
        respuesta = "LOGOUT_OK"
        respuesta_final = f"SEQ_ACK={seq}|{respuesta}"
        cache_respuestas[addr] = (seq, respuesta)
        sock.sendto(respuesta_final.encode(), addr)

    elif mensaje.startswith("CHAT|"):
        partes = mensaje.split("|", 3)
        if len(partes) == 4:
            remitente, destino, mensaje_chat = partes[1], partes[2], partes[3]

            # Si es un mensaje de desconexión
            es_desconexion = mensaje_chat.endswith("se desconectó del chat.")

            with lock:
                if destino in clientes_conectados:
                    ip_destino, port_destino = clientes_conectados[destino]

                    # Reenviamos con el remitente para que el cliente sepa de quién viene
                    sock.sendto(f"CHAT|{remitente}|{destino}|{mensaje_chat}".encode(), (ip_destino, port_destino))

                    # Solo confirmamos al remitente si no es desconexión
                    # Para desconexión podemos devolver algo como CHAT_BYE
                    respuesta = "CHAT_BYE" if es_desconexion else "CHAT_OK"
                else:
                    # Si el destinatario no está conectado
                    # Para desconexión no devolvemos error porque no es crítico
                    respuesta = "CHAT_BYE" if es_desconexion else "ERROR|Usuario no conectado."

            respuesta_final = f"SEQ_ACK={seq}|{respuesta}"
            cache_respuestas[addr] = (seq, respuesta)
            sock.sendto(respuesta_final.encode(), addr)

    elif mensaje.startswith("FILE|"):
        # Formato esperado: FILE|remitente|destino|nombre_archivo
        partes = mensaje.split("|", 3)
        if len(partes) == 4:
            remitente, destino, nombre_archivo = partes[1], partes[2], partes[3]
            with lock:
                if destino in clientes_conectados:
                    ip_destino, port_destino = clientes_conectados[destino]

                    # Reenviamos al destino
                    sock.sendto(f"FILE|{remitente}|{destino}|{nombre_archivo}".encode(), (ip_destino, port_destino))


                    # Confirmación al remitente
                    respuesta = "FILE_OK"
                else:
                    respuesta = "ERROR|Usuario no conectado."

            respuesta_final = f"SEQ_ACK={seq}|{respuesta}"
            cache_respuestas[addr] = (seq, respuesta)
            sock.sendto(respuesta_final.encode(), addr)

    elif mensaje.startswith("NOTIFY|"):
        try:
            _, destinatario, remitente = mensaje.split("|", 2)
            print('Destinatario: ', destinatario)

            if destinatario in clientes_conectados:
                direccion_destinatario = clientes_conectados[destinatario]
                mensaje_notify = f"NOTIFY|{remitente}"
                print('direccion: ', direccion_destinatario)
                sock.sendto(mensaje_notify.encode(), direccion_destinatario)
                print(f"[NOTIFY] Enviado a {destinatario} desde {remitente}")
                respuesta = f"SEQ_ACK={seq}|NOTIFY_OK"
            else:
                print(f"[NOTIFY] Usuario no disponible: {destinatario}")
                respuesta = f"SEQ_ACK={seq}|ERROR|Usuario no disponible"

            # Enviar el ACK solo al remitente original
            sock.sendto(respuesta.encode(), addr)

        except ValueError:
            print(f"[ERROR] Formato incorrecto en NOTIFY: {mensaje}")
            respuesta = f"SEQ_ACK={seq}|ERROR|Formato NOTIFY inválido"
            sock.sendto(respuesta.encode(), addr)


    elif mensaje.startswith("LS|"):
        partes = mensaje.split("|")
        usuario = partes[1]
        ruta_actual = directorios_actuales.get(usuario)

        if not ruta_actual or not os.path.exists(ruta_actual):
            respuesta = "ERROR|Directorio no encontrado."
            respuesta_final = f"SEQ_ACK={seq}|{respuesta}"
            cache_respuestas[addr] = (seq, respuesta)
            sock.sendto(respuesta_final.encode(), addr)
            return

        archivos = os.listdir(ruta_actual)
        respuesta = "LS"
        ruta_base = os.path.abspath(os.path.join("usuarios", usuario))

        if os.path.abspath(ruta_actual) != ruta_base:
            respuesta += "|.."

        if archivos:
            respuesta += "|" + "|".join(archivos)

        respuesta_final = f"SEQ_ACK={seq}|{respuesta}"
        cache_respuestas[addr] = (seq, respuesta)
        sock.sendto(respuesta_final.encode(), addr)


    elif mensaje.startswith("CD|"):
        partes = mensaje.split("|")
        if len(partes) != 3:
            respuesta = "ERROR|Formato inválido para CD"
            sock.sendto(f"SEQ_ACK={seq}|{respuesta}".encode(), addr)
            return

        usuario, ruta_relativa = partes[1], partes[2]
        ruta_base = os.path.abspath(os.path.join("usuarios", usuario))
        ruta_actual = directorios_actuales.get(usuario, ruta_base)
        nueva_ruta = os.path.abspath(os.path.normpath(os.path.join(ruta_actual, ruta_relativa)))

        if os.path.commonpath([ruta_base]) != os.path.commonpath([ruta_base, nueva_ruta]):
            respuesta = "ERROR|No se puede subir más allá del directorio raíz."
        elif not os.path.isdir(nueva_ruta):
            respuesta = "ERROR|Directorio no existe."
        else:
            directorios_actuales[usuario] = nueva_ruta
            relpath = os.path.relpath(nueva_ruta, ruta_base)
            respuesta = f"CD_OK|{relpath}"

        respuesta_final = f"SEQ_ACK={seq}|{respuesta}"
        cache_respuestas[addr] = (seq, respuesta)
        sock.sendto(respuesta_final.encode(), addr)
        print(f"[DEBUG CD] Usuario: {usuario}, Base: {ruta_base}, Actual: {ruta_actual}, Nueva: {nueva_ruta}")


    elif mensaje.startswith("GET_START|"):
        _, usuario, nombre = mensaje.split("|")
        ruta_actual = directorios_actuales.get(usuario)
        ruta_archivo = os.path.join(ruta_actual, nombre)

        if not os.path.exists(ruta_archivo):
            respuesta = "ERROR|Archivo no encontrado"
            cache_respuestas[addr] = (seq, respuesta)
            sock.sendto(f"SEQ_ACK={seq}|{respuesta}".encode(), addr)
            return

        with open(ruta_archivo, "rb") as f:
            contenido = f.read()
        bloques = [contenido[i:i+1024] for i in range(0, len(contenido), 1024)]

        archivos_en_envio[addr] = {
            "nombre": nombre,
            "bloques": bloques,
            "total": len(bloques),
            "actual": 0  # próximo bloque esperado
        }

        respuesta = f"GET_READY|{nombre}|{len(bloques)}"
        cache_respuestas[addr] = (seq, respuesta)
        sock.sendto(f"SEQ_ACK={seq}|{respuesta}".encode(), addr)

    elif mensaje.startswith("GET_ACK|"):
        _, usuario, nombre, bloque_id_str = mensaje.split("|")
        bloque_id = int(bloque_id_str)
        info = archivos_en_envio.get(addr)

        if info and info["nombre"] == nombre:
            if bloque_id == info["actual"]:
                # Enviar bloque correcto
                bloque = info["bloques"][bloque_id]
                data_b64 = base64.b64encode(bloque).decode()
                respuesta = f"GET_BLOCK|{nombre}|{bloque_id}|{data_b64}"
                sock.sendto(f"SEQ_ACK={seq}|{respuesta}".encode(), addr)
                cache_respuestas[addr] = (seq, respuesta)
                info["actual"] += 1

                if info["actual"] == info["total"]:
                    fin = f"GET_END|{nombre}"
                    sock.sendto(f"SEQ_ACK={seq}|{fin}".encode(), addr)
                    cache_respuestas[addr] = (seq, fin)
                    
            elif bloque_id == info["actual"] - 1:
                # REENVÍO del último bloque porque el cliente no recibió la respuesta
                print(f"[REINTENTO DETECTADO] Reenviando bloque {bloque_id} a {addr}")
                bloque = info["bloques"][bloque_id]
                data_b64 = base64.b64encode(bloque).decode()
                respuesta = f"GET_BLOCK|{nombre}|{bloque_id}|{data_b64}"
                sock.sendto(f"SEQ_ACK={seq}|{respuesta}".encode(), addr)
                cache_respuestas[addr] = (seq, respuesta)
            else:
                print(f"[GET_ACK] Ignorado: bloque {bloque_id} fuera de orden (esperado: {info['actual']})")

        else:
            print("[GET_ACK] No hay info activa de transferencia para este cliente")


    elif mensaje.startswith("GET_START_FROM|"):
        # Formato: GET_START_FROM|usuario_origen|ruta_relativa|archivo
        partes = mensaje.split("|", 4)
        if len(partes) == 4:
            usuario_origen, ruta_relativa, archivo = partes[1], partes[2], partes[3]
            ruta_base = os.path.join("usuarios", usuario_origen)
            ruta_archivo = os.path.normpath(os.path.join(ruta_base, ruta_relativa, archivo))

            if not ruta_archivo.startswith(ruta_base):
                sock.sendto("ERROR|Ruta no permitida".encode(), addr)
                return

            if not os.path.exists(ruta_archivo):
                print(ruta_archivo)
                sock.sendto("ERROR|Archivo no encontrado".encode(), addr)
                return

            tamaño = os.path.getsize(ruta_archivo)
            total_bloques = math.ceil(tamaño / 1024)
            respuesta = f"GET_READY_CHAT|{archivo}|{total_bloques}"
            sock.sendto(f'SEQ_ACK={seq}|{respuesta}'.encode(), addr)
        else:
            sock.sendto("ERROR|Formato incorrecto para GET_START_FROM".encode(), addr)

    elif mensaje.startswith("GET_ACK_FROM|"):
        # Formato: GET_ACK_FROM|usuario_origen|ruta_relativa|archivo|id_bloque
        partes = mensaje.split("|", 5)
        if len(partes) == 5:
            usuario_origen, ruta_relativa, archivo, id_bloque_str = partes[1], partes[2], partes[3], partes[4]
            ruta_base = os.path.join("usuarios", usuario_origen)
            ruta_archivo = os.path.normpath(os.path.join(ruta_base, ruta_relativa, archivo))

            if not ruta_archivo.startswith(ruta_base):
                sock.sendto("ERROR|Ruta no permitida".encode(), addr)
                return

            if not os.path.exists(ruta_archivo):
                sock.sendto("ERROR|Archivo no encontrado".encode(), addr)
                return

            bloque_id = int(id_bloque_str)
            with open(ruta_archivo, "rb") as f:
                f.seek(bloque_id * 1024)
                datos = f.read(1024)
                datos_b64 = base64.b64encode(datos).decode()
                respuesta = f"GET_BLOCK|{archivo}|{bloque_id}|{datos_b64}"
                sock.sendto(f'SEQ_ACK={seq}|{respuesta}'.encode(), addr)
        else:
            sock.sendto("ERROR|Formato incorrecto para GET_ACK_FROM".encode(), addr)

    elif mensaje.startswith("PUT_START|"):
        _, usuario, nombre, total_bloques = mensaje.split("|")
        ruta_actual = directorios_actuales[usuario]
        ruta_archivo = os.path.join(ruta_actual, nombre)
        archivos_en_recepcion[addr] = {
            "ruta": ruta_archivo,
            "total": int(total_bloques),
            "recibidos": {},
            "ack": -1
        }
        respuesta = "PUT_READY"
        cache_respuestas[addr] = (seq, respuesta)
        sock.sendto(f"SEQ_ACK={seq}|{respuesta}".encode(), addr)

    elif mensaje.startswith("PUT_BLOCK|"):
        _, usuario, nombre, bloque_id, data_b64 = mensaje.split("|", 4)
        bloque_id = int(bloque_id)
        data = base64.b64decode(data_b64)
        
        info = archivos_en_recepcion.get(addr)
        if info:
            info["recibidos"][bloque_id] = data
            info["ack"] = bloque_id
            sock.sendto(f"SEQ_ACK={seq}|ACK|{bloque_id}".encode(), addr)

    elif mensaje.startswith("PUT_END|"):
        info = archivos_en_recepcion.pop(addr, None)
        if info:
            with open(info["ruta"], "wb") as f:
                for i in range(info["total"]):
                    f.write(info["recibidos"].get(i, b""))  # maneja posibles huecos
            respuesta = "PUT_OK"
        else:
            respuesta = "ERROR|Transferencia incompleta"
        
        cache_respuestas[addr] = (seq, respuesta)
        sock.sendto(f"SEQ_ACK={seq}|{respuesta}".encode(), addr)


    elif mensaje.startswith("MKDIR|"):
        _, usuario, nombre = mensaje.split("|", 2)
        ruta_actual = directorios_actuales.get(usuario)
        nueva_carpeta = os.path.join(ruta_actual, nombre)
        try:
            os.mkdir(nueva_carpeta)
            respuesta = "MKDIR_OK"
        except Exception as e:
            respuesta = f"ERROR|{str(e)}"
        sock.sendto(f"SEQ_ACK={seq}|{respuesta}".encode(), addr)
        cache_respuestas[addr] = (seq, respuesta)

    elif mensaje.startswith("RMDIR|"):
        _, usuario, nombre = mensaje.split("|", 2)
        ruta_actual = directorios_actuales.get(usuario)
        carpeta = os.path.join(ruta_actual, nombre)
        try:
            os.rmdir(carpeta)
            respuesta = "RMDIR_OK"
        except Exception as e:
            respuesta = f"ERROR|{str(e)}"
        sock.sendto(f"SEQ_ACK={seq}|{respuesta}".encode(), addr)
        cache_respuestas[addr] = (seq, respuesta)

    elif mensaje.startswith("RM|"):
        _, usuario, nombre = mensaje.split("|", 2)
        ruta_actual = directorios_actuales.get(usuario)
        archivo = os.path.join(ruta_actual, nombre)
        try:
            os.remove(archivo)
            respuesta = "RM_OK"
        except Exception as e:
            respuesta = f"ERROR|{str(e)}"
        sock.sendto(f"SEQ_ACK={seq}|{respuesta}".encode(), addr)
        cache_respuestas[addr] = (seq, respuesta)
        
        
    else:
        respuesta = "ERROR|Comando inválido"
        respuesta_final = f"SEQ_ACK={seq}|{respuesta}"
        cache_respuestas[addr] = (seq, respuesta)
        sock.sendto(respuesta_final.encode(), addr)


def enviar_lista_conectados(sock):
    lista = ",".join(clientes_conectados.keys())
    b = f"CONNECTED|{lista}".encode()
    for addr in clientes_conectados.values():
        sock.sendto(b, addr)
        

def servidor():
    inicializar_bd()
    inicializar_directorios()
    for usuario, ruta in directorios_actuales.items():
        print(f"  - {usuario}: {ruta}")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((SERVER_IP, SERVER_PORT))
    print(f"Servidor UDP escuchando en {SERVER_IP}:{SERVER_PORT}")

    while True:
        try:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            print(f"Mensaje recibido de {addr}: {data}")
            threading.Thread(target=manejar_mensaje, args=(data, addr, sock), daemon=True).start()
        except Exception as e:
            print("Error en servidor:", e)

if __name__ == "__main__":
    servidor()
