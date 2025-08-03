import os
import socket
import threading
import base64

class ChatFTPClient:
    def __init__(self, server_ip: str, server_port: int, buffer_size: int = 4096):
        self.server_ip = server_ip
        self.server_port = server_port
        self.buffer_size = buffer_size
        self.reintentos = 5
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(5)
        self.seq_actual = 0
        self.username = None
        self.ruta_actual = []
        self.listeners = []

        threading.Thread(target=self._loop_escucha, daemon=True).start()

    def login(self, username: str):
        self.username = username

    def _loop_escucha(self):
        while True:
            try:
                data, _ = self.sock.recvfrom(self.buffer_size)
                mensaje = data.decode()
                for f in self.listeners:
                    f(mensaje)
            except:
                pass

    def _enviar_mensaje(self, mensaje: str) -> str:
        intentos = 0
        while intentos < self.reintentos:
            mensaje_completo = f"SEQ={self.seq_actual}|{mensaje}"
            try:
                self.sock.sendto(mensaje_completo.encode(), (self.server_ip, self.server_port))
                respuesta, _ = self.sock.recvfrom(self.buffer_size)
                respuesta_str = respuesta.decode()

                if respuesta_str.startswith(f"SEQ_ACK={self.seq_actual}|"):
                    self.seq_actual += 1
                    return respuesta_str.split("|", 1)[1]
            except socket.timeout:
                print(f"[INTENTO {intentos+1}] Timeout al enviar: {mensaje_completo}")
            intentos += 1
        return "ERROR|Timeout"

    def obtener_ruta_actual(self):
        return "/" + "/".join(self.ruta_actual) if self.ruta_actual else "/"

    def cambiar_directorio(self, subcarpeta: str) -> bool:
        resp = self._enviar_mensaje(f"CD|{self.username}|{subcarpeta}")
        if resp.startswith("CD_OK|"):
            if subcarpeta == ".." and self.ruta_actual:
                self.ruta_actual.pop()
            else:
                self.ruta_actual.append(subcarpeta)
            return True
        return False

    def listar_directorio(self):
        respuesta = self._enviar_mensaje(f"LS|{self.username}")
        if respuesta.startswith("LS|"):
            archivos = respuesta.split("|")[1:]
            archivos = [a for a in archivos if a.strip()]
            if not self.ruta_actual:
                archivos = [a for a in archivos if a != ".."]
            elif ".." not in archivos:
                archivos.insert(0, "..")
            return archivos
        return []

    def crear_directorio(self, nombre):
        return self._enviar_mensaje(f"MKDIR|{self.username}|{nombre}")

    def eliminar_directorio(self, nombre):
        return self._enviar_mensaje(f"RMDIR|{self.username}|{nombre}")

    def eliminar_archivo(self, nombre):
        return self._enviar_mensaje(f"RM|{self.username}|{nombre}")

    def subir_archivo(self, path_local):
        with open(path_local, "rb") as f:
            data = f.read()

        nombre = os.path.basename(path_local)
        bloques = [data[i:i+1024] for i in range(0, len(data), 1024)]

        self._enviar_mensaje(f"PUT_START|{self.username}|{nombre}|{len(bloques)}")
        for i, bloque in enumerate(bloques):
            data_b64 = base64.b64encode(bloque).decode()
            self._enviar_mensaje(f"PUT_BLOCK|{self.username}|{nombre}|{i}|{data_b64}")
        return self._enviar_mensaje(f"PUT_END|{self.username}|{nombre}")

    def descargar_archivo(self, nombre, destino):
        respuesta = self._enviar_mensaje(f"GET_START|{self.username}|{nombre}")
        if not respuesta.startswith("GET_READY"):
            raise Exception("Error al iniciar descarga")
        _, _, total_str = respuesta.split("|")
        total_bloques = int(total_str)
        bloques = {}

        for i in range(total_bloques):
            for intento in range(5):
                resp = self._enviar_mensaje(f"GET_ACK|{self.username}|{nombre}|{i}")
                if resp.startswith("GET_BLOCK|"):
                    _, _, id_str, data_b64 = resp.split("|", 3)
                    if int(id_str) == i:
                        bloques[i] = base64.b64decode(data_b64)
                        break
            else:
                raise Exception(f"Bloque {i} no recibido")

        with open(destino, "wb") as f:
            for i in range(total_bloques):
                f.write(bloques.get(i, b""))

    def descargar_de_usuario(self, usuario_origen, nombre, ruta_remota, destino_local):
        resp = self._enviar_mensaje(f"GET_START_FROM|{usuario_origen}|{ruta_remota}|{nombre}")
        print(f'Esto es el rest: {resp}')
        if not resp.startswith("GET_READY_CHAT"):
            raise Exception("Fallo al iniciar GET_FROM")
        _, _, total_str = resp.split("|")
        total_bloques = int(total_str)
        bloques = {}

        for i in range(total_bloques):
            for intento in range(5):
                r = self._enviar_mensaje(
                    f"GET_ACK_FROM|{usuario_origen}|{ruta_remota}|{nombre}|{i}"
                )
                print(f"[DEBUG] Respuesta recibida: {r} → {r.split('|')}")
                if r.startswith("GET_BLOCK"):
                    partes = r.split("|", 3)
                    if len(partes) == 4:
                        _, _, id_str, data_b64 = partes
                        if int(id_str) == i:
                            bloques[i] = base64.b64decode(data_b64)
                            break
                    else:
                        print(f"[ERROR] Formato inesperado en GET_BLOCK: {r}")

            else:
                raise Exception(f"Bloque {i} no recibido")

        with open(destino_local, "wb") as f:
            for i in range(total_bloques):
                f.write(bloques.get(i, b""))

    def iniciar_escucha(self, callback):
        if callback not in self.listeners:
            self.listeners.append(callback)

    def procesar_notify(self, mensaje: str) -> str | None:
        try:
            partes = mensaje.split("|")
            if len(partes) == 2 and partes[0] == "NOTIFY" and partes[1] != self.username:
                return partes[1]
        except:
            pass
        return None
