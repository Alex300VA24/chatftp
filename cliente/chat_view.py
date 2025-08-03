import flet as ft
import os

class ChatView:
    def __init__(self, user, page: ft.Page, nome: str, destinatario: str = None):
        self.page = page
        self.nome = nome
        self.user = user
        self.destinatario = destinatario

        self.lista_archivos = ft.ListView(expand=True, spacing=5, padding=5, auto_scroll=False)
        self.mensajes = ft.ListView(expand=True, spacing=10, padding=10, auto_scroll=True)
        self.mensaje_input = ft.TextField(hint_text="Escribir un mensaje...", expand=True)
        self.destino_input = ft.TextField(
            label="Destinatario",
            width=200,
            value=self.destinatario if self.destinatario else ""
        )

        self.page.window.prevent_close = True

        self.inicializar()


    def inicializar(self):
        self.page.controls.clear()
        self.page.title = "Chat + Archivos"
        self.page.window_width = 800
        self.page.window_height = 600

        self.cargar_archivos()
        self.configurar_escucha()

        layout = ft.Row([
            ft.Column([self.lista_archivos], width=200, expand=True),
            ft.Column([
                ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=self.volver_home),
                    self.destino_input
                ]),
                self.mensajes,
                ft.Row([
                    self.mensaje_input,
                    ft.IconButton(icon=ft.Icons.SEND, on_click=self.enviar_click)
                ])
            ], expand=True)
        ], expand=True)

        self.page.add(layout)
        self.page.update()

        return self.mensajes

    def cargar_archivos(self):
        self.lista_archivos.controls.clear()
        archivos = self.user.listar_directorio()

        if not archivos:
            self.lista_archivos.controls.append(ft.Text("Directorio vacío", color=ft.Colors.GREY))
        else:
            for archivo in archivos:
                if archivo == "..":
                    self.lista_archivos.controls.append(
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.FOLDER_OPEN),
                            title=ft.Text(".."),
                            on_click=lambda e, a="..", folder=True: self.manejar_click_archivo(a, folder)
                        )
                    )
                    continue

                is_folder = "." not in archivo
                icono = ft.Icons.FOLDER if is_folder else ft.Icons.INSERT_DRIVE_FILE
                self.lista_archivos.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(icono, size=18),
                        title=ft.Text(archivo),
                        on_click=lambda e, a=archivo, folder=is_folder: self.manejar_click_archivo(a, folder)
                    )
                )

        self.page.update()

    def manejar_click_archivo(self, nombre, es_carpeta):
        if es_carpeta:
            if self.user.cambiar_directorio(nombre):
                self.cargar_archivos()
        else:
            destino = self.destino_input.value.strip()
            if not destino:
                self.mensajes.controls.append(ft.Text("⚠ Primero selecciona un destinatario.", color=ft.Colors.RED))
                self.page.update()
                return
            ruta_rel = os.path.join(*self.user.ruta_actual) if self.user.ruta_actual else "."
            self.user._enviar_mensaje(f"FILE|{self.nome}|{destino}|{nombre}|{ruta_rel}")
            self.mensajes.controls.append(ft.Text(f"Tú enviaste '{nombre}'", color=ft.Colors.BLUE))
            self.page.update()

    def enviar_click(self, e):
        texto = self.mensaje_input.value.strip()
        destino = self.destino_input.value.strip()
        if texto and destino:
            self.user._enviar_mensaje(f"CHAT|{self.nome}|{destino}|{texto}")
            self.mensajes.controls.append(ft.Text(f"Tú: {texto}", color=ft.Colors.BLUE))
            self.mensaje_input.value = ""
            self.page.update()

    def configurar_escucha(self):
        self.user.iniciar_escucha(self.recibir_mensaje_chat)

    def recibir_mensaje_chat(self, data):
        if data.startswith("CHAT|"):
            partes = data.split("|", 3)
            if len(partes) == 4:
                origen, destino, contenido = partes[1], partes[2], partes[3]
                if destino == self.nome:
                    self.mensajes.controls.append(ft.Text(f"{origen}: {contenido}", color=ft.Colors.GREEN))
                    self.page.update()
        elif data.startswith("FILE|"):
            partes = data.split("|", 4)
            if len(partes) == 5:
                origen, destino, nombre_archivo, ruta_remota = partes[1:]
                if destino == self.nome:
                    self.mensajes.controls.append(ft.Container(
                        content=ft.Column([
                            ft.Text(f"{origen} te envió: {nombre_archivo}"),
                            ft.TextButton("Descargar", on_click=lambda e: self.descargar_archivo_chat(origen, nombre_archivo, ruta_remota))
                        ]),
                        border=ft.Border(
                        left=ft.BorderSide(1, ft.Colors.BLACK),
                        top=ft.BorderSide(1, ft.Colors.BLACK),
                        right=ft.BorderSide(1, ft.Colors.BLACK),
                        bottom=ft.BorderSide(1, ft.Colors.BLACK)
                    ),
                        padding=5
                    ))
                    self.page.update()

    def descargar_archivo_chat(self, origen, nombre_archivo, ruta_remota):
        try:
            carpeta_destino = os.path.join(os.getcwd(), "descargas_chat")
            os.makedirs(carpeta_destino, exist_ok=True)
            destino_local = os.path.join(carpeta_destino, nombre_archivo)

            self.user.descargar_de_usuario(origen, nombre_archivo, ruta_remota, destino_local)
            respuesta = self.user.subir_archivo(destino_local)
            if respuesta.startswith("PUT_OK"):
                self.mensajes.controls.append(ft.Text(f"✅ Archivo recibido y subido: {nombre_archivo}", color=ft.Colors.GREY))
            else:
                self.mensajes.controls.append(ft.Text(f"⚠️ Recibido pero error al subir: {respuesta}", color=ft.Colors.ORANGE))
            self.cargar_archivos()
        except Exception as e:
            self.mensajes.controls.append(ft.Text(f"❌ Error: {e}", color=ft.Colors.RED))
        finally:
            self.page.update()

    def volver_home(self, e):
        destino = self.destino_input.value.strip()
        if destino:
            self.user._enviar_mensaje(f"CHAT|{self.nome}|{destino}|{self.nome} se desconectó del chat.")
        from home_view import HomeView
        HomeView(self.page, self.user, self.nome).mostrar()


# Para usarla:
# ChatView(page, "julio", "maria")
