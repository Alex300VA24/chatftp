import socket
import threading
import os
from auth import inicializar_bd, registrar_usuario, verificar_credenciales, activar_usuario, desactivar_usuario
from utils import inicializar_directorios, directorios_actuales


SERVER_IP = "0.0.0.0"
SERVER_PORT = 2121
BUFFER_SIZE = 4096

clientes_conectados = {}  # usuario: (ip, port)
lock = threading.Lock()

# Diccionario para llevar el directorio actual de cada usuario
directorios_actuales = {}
cache_respuestas = {}

def manejar_mensaje(data, addr, sock):
    mensaje_completo = data.decode()
    if not mensaje_completo.startswith("SEQ="):
        respuesta = "ERROR|Falta número de secuencia (SEQ)"
        respuesta_final = f"SEQ_ACK={seq}|{respuesta}"
        cache_respuestas[addr] = (seq, respuesta)
        sock.sendto(respuesta_final.encode(), addr)
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
        usuario = mensaje.split("|")[1]
        desactivar_usuario(usuario)
        with lock:
            if usuario in clientes_conectados:
                del clientes_conectados[usuario]
        respuesta = "LOGOUT_OK"
        respuesta_final = f"SEQ_ACK={seq}|{respuesta}"
        cache_respuestas[addr] = (seq, respuesta)
        sock.sendto(respuesta_final.encode(), addr)




    elif mensaje.startswith("CHAT|"):
        partes = mensaje.split("|", 2)
        if len(partes) == 3:
            destino, mensaje_chat = partes[1], partes[2]
            with lock:
                if destino in clientes_conectados:
                    ip_destino, port_destino = clientes_conectados[destino]
                    sock.sendto(f"CHAT|{partes[1]}|{mensaje_chat}".encode(), (ip_destino, port_destino))

                    # Confirmación al remitente
                    respuesta = "CHAT_OK"
                else:
                    respuesta = "ERROR|Usuario no conectado."

            respuesta_final = f"SEQ_ACK={seq}|{respuesta}"
            cache_respuestas[addr] = (seq, respuesta)
            sock.sendto(respuesta_final.encode(), addr)

    
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

        
    elif mensaje.startswith("GET|"):
        pass

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
