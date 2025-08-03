#server_chatftp


# Importacao de bibliotecas
import socket
import threading
import os
import math
import base64
from auth import inicializar_bd, registrar_usuario, verificar_credenciales, activar_usuario, desactivar_usuario
from utils import inicializar_directorios, directorios_actuales


# Class ServerChatFTP
class ServerChatFTP:
    def __init__(self, ip="0.0.0.0", port=2121, buffer_size=4096):
        self.ip = ip
        self.port = port
        self.buffer_size = buffer_size
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.lock = threading.Lock()

        self.clientes_conectados = {}  # usuario: (ip, port)
        self.archivos_en_recepcion = {}
        self.archivos_en_envio = {}
        self.cache_respuestas = {}
        self.directorios_actuales = {}

    # Iniciar servidor, banco de dados e diretórios
    def start(self):
        inicializar_bd()
        inicializar_directorios()

        self.sock.bind((self.ip, self.port))
        print(f"Servidor UDP escuchando en {self.ip}:{self.port}")

        while True:
            try:
                data, addr = self.sock.recvfrom(self.buffer_size)
                threading.Thread(target=self.handle_message, args=(data, addr), daemon=True).start()
            except Exception as e:
                print("Error en servidor:", e)


    def handle_message(self, data, addr):
        try:
            mensaje_completo = data.decode()
            if not mensaje_completo.startswith("SEQ="):
                self.send(addr, "ERROR|Falta número de secuencia (SEQ)", seq=None)
                return

            try:
                encabezado, mensaje = mensaje_completo.split("|", 1)
                seq = int(encabezado.split("=")[1])
            except:
                self.send(addr, "ERROR|Formato inválido de SEQ", seq=0)
                return

            # Reintento
            ultimo_seq, ultima_respuesta = self.cache_respuestas.get(addr, (-1, None))
            if seq == ultimo_seq:
                print(f"[REINTENTO] Reenviando SEQ={seq} a {addr}")
                self.send(addr, ultima_respuesta, seq)
                return

            # Registrar nuevo SEQ
            print(f"[RECEIVED] {addr} → {mensaje}")
            respuesta = self.dispatch_command(mensaje, addr, seq)
            self.cache_respuestas[addr] = (seq, respuesta)

            if respuesta:
                self.send(addr, respuesta, seq)
        except Exception as e:
            print("[ERROR] en handle_message:", e)

    # Incluir 'SEQ_ACK='
    def send(self, addr, mensaje, seq):
        if seq is not None:
            mensaje = f"SEQ_ACK={seq}|{mensaje}"
        self.sock.sendto(mensaje.encode(), addr)

    def dispatch_command(self, mensaje, addr, seq):
        if mensaje.startswith("REGISTER|"):
            return self.cmd_register(mensaje)
        elif mensaje.startswith("LOGIN|"):
            return self.cmd_login(mensaje, addr)
        elif mensaje.startswith("LOGOUT|"):
            return self.cmd_logout(mensaje)
        elif mensaje.startswith("CHAT|"):
            return self.cmd_chat(mensaje)
        elif mensaje.startswith("LS|"):
            return self.cmd_ls(mensaje)
        elif mensaje.startswith("CD|"):
            return self.cmd_cd(mensaje)
        elif mensaje.startswith("PUT_START|"):
            return self.cmd_put_start(mensaje, addr)
        elif mensaje.startswith("PUT_BLOCK|"):
            return self.cmd_put_block(mensaje, addr)
        elif mensaje.startswith("PUT_END|"):
            return self.cmd_put_end(addr)
        elif mensaje.startswith("MKDIR|"):
            return self.cmd_mkdir(mensaje)
        elif mensaje.startswith("RMDIR|"):
            return self.cmd_rmdir(mensaje)
        elif mensaje.startswith("RM|"):
            return self.cmd_rm(mensaje)
        elif mensaje.startswith("GET_START|"):
            return self.cmd_get_start(mensaje, addr, seq)
        elif mensaje.startswith("GET_ACK|"):
            return self.cmd_get_ack(mensaje, addr, seq)
        elif mensaje.startswith("FILE|"):
            return self.cmd_file(mensaje)
        elif mensaje.startswith("NOTIFY|"):
            return self.cmd_notify(mensaje)
        elif mensaje.startswith("GET_START_FROM|"):
            return self.cmd_get_star_from(mensaje)
        elif mensaje.startswith("GET_ACK_FROM|"):
            return self.cmd_get_ack_from(mensaje)
        # ... otros comandos como FILE|, NOTIFY|, GET_START_FROM|, etc.
        else:
            return "ERROR|Comando inválido"


    # Implementando comandos
    def cmd_register(self, mensaje):
        _, username, password = mensaje.split("|")
        return registrar_usuario(username, password)

    def cmd_login(self, mensaje, addr):
        _, username, password = mensaje.split("|")
        if verificar_credenciales(username, password):
            activar_usuario(username)
            with self.lock:
                self.clientes_conectados[username] = addr
            ruta = os.path.join("usuarios", username)
            if not os.path.exists(ruta):
                os.makedirs(ruta)
            self.directorios_actuales[username] = os.path.abspath(ruta)
            return "LOGIN_OK"
        return "ERROR|Credenciales inválidas"

    def cmd_logout(self, mensaje):
        _, username = mensaje.split("|")
        desactivar_usuario(username)
        with self.lock:
            self.clientes_conectados.pop(username, None)
            self.directorios_actuales.pop(username, None)
        return "LOGOUT_OK"

    def cmd_chat(self, mensaje):
        _, remitente, destino, texto = mensaje.split("|", 3)
        es_desconexion = texto.endswith("se desconectó del chat.")
        with self.lock:
            if destino in self.clientes_conectados:
                ip_dest, port_dest = self.clientes_conectados[destino]
                self.sock.sendto(f"CHAT|{remitente}|{destino}|{texto}".encode(), (ip_dest, port_dest))
                return "CHAT_BYE" if es_desconexion else "CHAT_OK"
            return "CHAT_BYE" if es_desconexion else "ERROR|Usuario no conectado."

    def cmd_file(self, mensaje):
        _, remitente, destino, texto = mensaje.split('|', 3)
        with self.lock:
            if destino in  self.clientes_conectados:
                ip_dest, port_dest = self.clientes_conectados[destino]
                self.sock.sendto(f"FILE|{remitente}|{destino}|{texto}".encode(), (ip_dest, port_dest))
                return 'FILE_OK'
            return "ERROR|Usuario no conectado."
        
    def cmd_notify(self, mensaje):
        _, destino, remitente = mensaje.split('|', 2)
        if destino in self.clientes_conectados:
            direc_destino = self.clientes_conectados[destino]
            self.sock.sendto(f"NOTIFY|{remitente}".encode(), direc_destino)
            return 'NOTIFY_OK'
        else:
            return 'ERROR|Usuario no disponible'

    def cmd_ls(self, mensaje):
        _, usuario = mensaje.split("|")
        ruta = self.directorios_actuales.get(usuario)
        if not ruta or not os.path.exists(ruta):
            return "ERROR|Directorio no encontrado."
        archivos = os.listdir(ruta)
        base = os.path.abspath(os.path.join("usuarios", usuario))
        respuesta = "LS"
        if os.path.abspath(ruta) != base:
            respuesta += "|.."
        if archivos:
            respuesta += "|" + "|".join(archivos)
        return respuesta

    def cmd_cd(self, mensaje):
        _, usuario, ruta_rel = mensaje.split("|")
        base = os.path.abspath(os.path.join("usuarios", usuario))
        actual = self.directorios_actuales.get(usuario, base)
        nueva = os.path.abspath(os.path.join(actual, ruta_rel))
        if os.path.commonpath([base]) != os.path.commonpath([base, nueva]):
            return "ERROR|No se puede subir más allá del directorio raíz."
        if not os.path.isdir(nueva):
            return "ERROR|Directorio no existe."
        self.directorios_actuales[usuario] = nueva
        relpath = os.path.relpath(nueva, base)
        return f"CD_OK|{relpath}"
    
    def cmd_get_start(self, mensaje, addr, seq):
        _, usuario, nombre = mensaje.split("|")
        actual = self.directorios_actuales.get(usuario)
        ruta_archivo = os.path.join(actual, nombre)
        if not os.path.exists(ruta_archivo):
            respuesta = "ERROR|Archivo no encontrado"
            self.cache_respuestas[addr] = (seq, respuesta)
            return respuesta
        with open(ruta_archivo, 'rb') as f:
            contenido = f.read()
        bloques = [contenido[i:i+1024] for i in range(0, len(contenido), 1024)]
        self.archivos_en_envio[addr] = {
            "nombre": nombre,
            "bloques": bloques,
            "total": len(bloques),
            "actual": 0  # próximo bloque esperado
        }
        respuesta = f"GET_READY|{nombre}|{len(bloques)}"
        return respuesta
        
    def cmd_get_ack(self, mensaje, addr, seq):
        _, usuario, nombre, bloque_id_str = mensaje.split("|")
        bloque_id = int(bloque_id_str)
        info = self.archivos_en_envio.get(addr)
        if info and info['nombre'] == nombre:
            if bloque_id == info['actual']:
                bloque = info['bloques'][bloque_id]
                data_b64 = base64.b64encode(bloque).decode()
                respuesta = f"GET_BLOCK|{nombre}|{bloque_id}|{data_b64}"
                self.cache_respuestas[addr] = (seq, respuesta)
                info["actual"] += 1
                if info["actual"] == info["total"]:
                    fin = f"GET_END|{nombre}"
                    self.cache_respuestas[addr] = (seq, fin)
                    return fin
                return respuesta
        
            elif bloque_id == info['actual'] - 1:
                bloque = info["bloques"][bloque_id]
                data_b64 = base64.b64encode(bloque).decode()
                respuesta = f"GET_BLOCK|{nombre}|{bloque_id}|{data_b64}"
                self.cache_respuestas[addr] = (seq, respuesta)
                return respuesta
        
    def cmd_get_star_from(self, mensaje):
        _, usuario, ruta_rel, archivo = mensaje.split('|')
        ruta_base = os.path.join('usuarios', usuario)
        ruta_archivo = os.path.normpath(os.path.join(ruta_base, ruta_rel, archivo))       

        if not ruta_archivo.startswith(ruta_base):
            return "ERROR|Ruta no permitida"
        if not os.path.exists(ruta_archivo):
            return "ERROR|Archivo no encontrado"
        
        tamaño = os.path.getsize(ruta_archivo)
        total_bloques = math.ceil(tamaño / 1024)
        respuesta = f"GET_READY_CHAT|{archivo}|{total_bloques}"
        return respuesta
    
    def cmd_get_ack_from(self, mensaje):
        partes = mensaje.split("|")
        if len(partes) != 5:
            return "ERROR|Formato inválido en GET_ACK_FROM"
        _, usuario, ruta_rel, archivo, id_bloque_str = partes

        ruta_base = os.path.join("usuarios", usuario)
        ruta_archivo = os.path.normpath(os.path.join(ruta_base, ruta_rel, archivo))

        if not ruta_archivo.startswith(ruta_base):
            return "ERROR|Ruta no permitida"

        if not os.path.exists(ruta_archivo):
            return "ERROR|Archivo no encontrado"
        
        bloque_id = int(id_bloque_str)
        with open(ruta_archivo, "rb") as f:
            f.seek(bloque_id * 1024)
            datos = f.read(1024)
            datos_b64 = base64.b64encode(datos).decode()
            respuesta = f"GET_BLOCK|{archivo}|{bloque_id}|{datos_b64}"
            return respuesta

    def cmd_put_start(self, mensaje, addr):
        _, usuario, nombre, total = mensaje.split("|")
        ruta = os.path.join(self.directorios_actuales[usuario], nombre)
        self.archivos_en_recepcion[addr] = {
            "ruta": ruta, "total": int(total), "recibidos": {}, "ack": -1
        }
        return "PUT_READY"

    def cmd_put_block(self, mensaje, addr):
        _, usuario, nombre, bloque_id, data_b64 = mensaje.split("|", 4)
        bloque_id = int(bloque_id)
        data = base64.b64decode(data_b64)
        info = self.archivos_en_recepcion.get(addr)
        if info:
            info["recibidos"][bloque_id] = data
            info["ack"] = bloque_id
            self.sock.sendto(f"ACK|{bloque_id}".encode(), addr)
        return None

    def cmd_put_end(self, addr):
        info = self.archivos_en_recepcion.pop(addr, None)
        if not info:
            return "ERROR|Transferencia incompleta"
        with open(info["ruta"], "wb") as f:
            for i in range(info["total"]):
                f.write(info["recibidos"].get(i, b""))
        return "PUT_OK"

    def cmd_mkdir(self, mensaje):
        _, usuario, nombre = mensaje.split("|")
        ruta = os.path.join(self.directorios_actuales[usuario], nombre)
        try:
            os.mkdir(ruta)
            return "MKDIR_OK"
        except Exception as e:
            return f"ERROR|{str(e)}"

    def cmd_rmdir(self, mensaje):
        _, usuario, nombre = mensaje.split("|")
        ruta = os.path.join(self.directorios_actuales[usuario], nombre)
        try:
            os.rmdir(ruta)
            return "RMDIR_OK"
        except Exception as e:
            return f"ERROR|{str(e)}"

    def cmd_rm(self, mensaje):
        _, usuario, nombre = mensaje.split("|")
        ruta = os.path.join(self.directorios_actuales[usuario], nombre)
        try:
            os.remove(ruta)
            return "RM_OK"
        except Exception as e:
            return f"ERROR|{str(e)}"
    
    def enviar_lista_conectados(self, addr):
        lista = ",".join(self.clientes_conectados.keys())
        b = f"CONNECTED|{lista}".encode()
        for addr in self.clientes_conectados.values():
            self.sock.sendto(b, addr)

if __name__ == "__main__":
    server = ServerChatFTP()
    server.start()