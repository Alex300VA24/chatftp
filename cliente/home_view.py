import flet as ft
import os
import sys
import time
from chat_view import ChatView

# Agrega el path del directorio raíz del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from servidor import auth


class HomeView:
    def __init__(self, page: ft.Page, user, nome):
        self.page = page
        self.user = user
        self.nome = nome
        self.lista_directorio = ft.Column(spacing=5)
        self.output_text = ft.Text("", size=18)
        self.ruta_label = ft.Text("", size=13, italic=True, color=ft.Colors.BLUE_GREY)
        self.input_box = ft.TextField(label="Comando FTP", width=400)
        self.processing = False

        self.page.window.prevent_close = True

        self._animar_texto = False  # Controlador del bucle de puntos


    def animar_output_texto(self, texto_base="Subiendo archivo"):
        relojes = ["🕛", "🕒", "🕔", "🕕", "🕗", "🕘", "🕙", "🕚"]
        puntos = [".", "..", "..."]

        def animacion():
            i = 0
            while self._animar_texto:
                puntos_actuales = puntos[i % len(puntos)]
                reloj_actual = relojes[i % len(relojes)]
                self.output_text.value = f"{texto_base} {puntos_actuales} {reloj_actual}"
                self.page.update()
                time.sleep(0.5)
                i += 1

        self.page.run_thread(animacion)


    def mostrar(self):
        self.user.iniciar_escucha(self.recibir_mensaje_home)

        self.page.title = "MyFTP - Panel Principal"
        self.page.window_width = 600
        self.page.window_height = 600
        self.page.scroll = ft.ScrollMode.AUTO

        barra_herramientas = ft.Row([
            ft.IconButton(icon=ft.Icons.CREATE_NEW_FOLDER, tooltip="Crear carpeta", on_click=self.crear_carpeta),
            ft.IconButton(icon=ft.Icons.DELETE, tooltip="Eliminar", on_click=self.eliminar_item),
            ft.IconButton(icon=ft.Icons.UPLOAD_FILE, tooltip="Subir archivo", on_click=self.subir_archivo_desde_dialogo),
            ft.IconButton(icon=ft.Icons.DOWNLOAD, tooltip="Descargar archivo", on_click=self.descargar_archivo_dialogo)
        ], alignment=ft.MainAxisAlignment.START)

        panel_contenido = ft.Column([
            barra_herramientas,
            self.ruta_label,
            self.lista_directorio,
            ft.Divider(),
            self.output_text
        ], expand=True)

        usuarios_activos = auth.obtener_usuarios_activos()
        lista_usuarios = self.construir_lista_usuarios(self.nome, usuarios_activos, self.notificar_usuario)

        etiqueta_usuarios = ft.Text('Lista de usuarios conectados', color=ft.Colors.WHITE)

        layout = ft.Row([
            ft.Container(content=lista_usuarios, padding=10, width=150, bgcolor=ft.Colors.GREY_200),
            ft.VerticalDivider(width=1),
            ft.Container(content=panel_contenido, padding=10, expand=True)
        ], expand=True)

        self.page.controls.clear()
        self.page.add(etiqueta_usuarios,layout, ft.Button("Cerrar Session", on_click=self.logout))
        self.cargar_directorio()
        self.page.update()

    def recibir_mensaje_home(self, mensaje: str):
        if mensaje.startswith("NOTIFY|"):
            remitente = self.user.procesar_notify(mensaje)
            if remitente:
                self.mostrar_dialogo_notify(remitente)

    def mostrar_dialogo_notify(self, remitente):
        def cerrar_dialogo(e=None):
            dialogo.open = False
            self.page.update()

        def aceptar_chat(e=None):
            dialogo.open = False
            from chat_view import ChatView
            mensajes = ChatView(self.user, self.page, nome=self.nome, destinatario=remitente).inicializar()
            mensaje_conexion = "Está conectado al chat"
            self.user._enviar_mensaje(f"CHAT|{self.nome}|{remitente}|{mensaje_conexion}")
            mensajes.controls.append(ft.Text(f"{remitente}: {mensaje_conexion}", color=ft.Colors.GREEN))
            self.page.update()

        dialogo = ft.AlertDialog(
            title=ft.Text("Solicitud de chat privado", weight=ft.FontWeight.BOLD),
            content=ft.Text(f"{remitente} quiere hablar contigo."),
            actions=[
                ft.TextButton("Cerrar", style=ft.ButtonStyle(color=ft.Colors.ERROR), on_click=cerrar_dialogo),
                ft.FilledButton("Aceptar", icon=ft.Icons.CHAT, on_click=aceptar_chat)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=10)
        )
        self.page.overlay.clear()
        self.page.overlay.append(dialogo)
        dialogo.open = True
        self.page.update()

    def cargar_directorio(self):
        def tarea():
            self._animar_texto = True
            self.animar_output_texto("Cargando directorio")

            try:
                items = self.user.listar_directorio()
                self.lista_directorio.controls.clear()

                if not items:
                    self.lista_directorio.controls.append(
                        ft.Text("Directorio vacío", color=ft.Colors.GREY_400)
                    )
                else:
                    for item in items:
                        if item == "..":
                            self.lista_directorio.controls.append(
                                ft.ListTile(
                                    title=ft.Text(".."),
                                    leading=ft.Icon(ft.Icons.FOLDER_OPEN),
                                    on_click=lambda e, x="..": self.navegar(x),
                                )
                            )
                            continue

                        is_folder = "." not in item
                        icono = ft.Icons.FOLDER if is_folder else ft.Icons.INSERT_DRIVE_FILE
                        color_icono = ft.Colors.AMBER_300 if is_folder else ft.Colors.BLUE_300

                        self.lista_directorio.controls.append(
                            ft.ListTile(
                                title=ft.Text(item, overflow=ft.TextOverflow.ELLIPSIS),
                                leading=ft.Icon(icono, color=color_icono),
                                on_click=lambda e, x=item: self.navegar(x),
                                dense=True,
                                hover_color=ft.Colors.with_opacity(0.1, ft.Colors.PRIMARY),
                            )
                        )

                self.ruta_label.value = f"📂 Ruta: {self.user.obtener_ruta_actual()}"

            except Exception as ex:
                self.output_text.value = f"❌ Error cargando directorio: {str(ex)}"
            finally:
                self.output_text.value = ""
                self._animar_texto = False
                self.page.update()

        self.page.run_thread(tarea)


    def navegar(self, nombre):
        if self.processing:
            return
        self.processing = True
        try:
            if nombre == "..":
                if self.user.cambiar_directorio(".."):
                    self.output_text.value = "Subiste un nivel."
                    self.cargar_directorio()
            elif "." not in nombre:
                if self.user.cambiar_directorio(nombre):
                    self.output_text.value = f"Entraste a '{nombre}'"
                    self.cargar_directorio()
                else:
                    self.output_text.value = f"Error al entrar a '{nombre}'"
            else:
                self.output_text.value = f"'{nombre}' es un archivo."
            self.page.update()
        finally:
            self.processing = False

    def abrir_chat(self, e):
        self._animar_texto = True
        self.animar_output_texto("Abriendo chat")

        def tarea():
            try:
                from chat_view import ChatView
                ChatView(self.user, self.page, username=self.nome, destinatario=self.destinatario).inicializar()
            except Exception as ex:
                self.output_text.value = f"❌ Error al abrir el chat: {str(ex)}"
            finally:
                self._animar_texto = False
                self.page.update()

        self.page.run_thread(tarea)


    def logout(self, e):
        self._animar_texto = True
        self.animar_output_texto("Cerrando sesión")

        def tarea():
            try:
                self.user._enviar_mensaje(f"LOGOUT|{self.nome}")
            except Exception as ex:
                self.output_text.value = f"❌ Error al cerrar sesión: {str(ex)}"
                return
            finally:
                self._animar_texto = False

            from login_view import LoginView
            self.page.controls.clear()
            LoginView(self.page, self.user).mostrar()

        self.page.run_thread(tarea)


    def crear_carpeta(self, e):
        # Crear controles del diálogo
        input_nombre = ft.TextField(
            label="Nombre de la carpeta",
            autofocus=True,
            hint_text="Ej: MiProyecto",
            capitalization=ft.TextCapitalization.WORDS,
            border_color=ft.Colors.PRIMARY
        )
        # Funciones de manejo
        def cerrar_dialogo(e=None):
            main_dialog.open = False
            self.page.update()
        
        def confirmar_creacion(e):
            nombre = input_nombre.value.strip()
            print(f'Intento de creación: "{nombre}"')
            
            if not nombre:
                error_dialog = ft.AlertDialog(
                    title=ft.Text("Error", color=ft.Colors.ERROR),
                    content=ft.Text("Debe ingresar un nombre válido"),
                    actions=[
                        ft.TextButton("Entendido", on_click=lambda e: (setattr(error_dialog, 'open', False), self.page.update()))
                    ],
                    shape=ft.RoundedRectangleBorder(radius=8)
                )
                self.page.overlay.append(error_dialog)
                error_dialog.open = True
                self.page.update()
                return 
            try:
                # Ejecutar comando FTP
                self.user.crear_directorio(nombre)
                respuesta = f"Carpeta '{nombre}' creada correctamente."
                print(f"Respuesta del servidor: {respuesta}")
                
                # Actualizar interfaz
                self.output_text.value = respuesta
                self.cargar_directorio()
                cerrar_dialogo()
                
                # Mostrar notificación de éxito
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Carpeta '{nombre}' creada", color=ft.Colors.ON_PRIMARY),
                    bgcolor=ft.Colors.PRIMARY
                )
                self.page.snack_bar.open = True
                self.page.update()
                
            except Exception as ex:
                print(f"Error al crear carpeta: {ex}")
                self.output_text.value = f"Error: {str(ex)}"
                self.page.update()

        # 4. Configurar diálogo principal
        main_dialog = ft.AlertDialog(
            title=ft.Text("Nueva Carpeta", weight=ft.FontWeight.BOLD),
            content=ft.Column([
                input_nombre,
                ft.Text("Ingrese un nombre sin caracteres especiales", size=12, color=ft.Colors.GREY)
            ], tight=True),
            actions=[
                ft.TextButton("Cancelar", 
                    style=ft.ButtonStyle(color=ft.Colors.ERROR),
                    on_click=cerrar_dialogo
                ),
                ft.FilledButton("Crear",
                    icon=ft.Icons.CREATE_NEW_FOLDER,
                    on_click=confirmar_creacion
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=10)
        )
        
        # 5. Mostrar diálogo (nuevo método para Flet >= 0.26.0)
        self.page.overlay.clear()
        self.page.overlay.append(main_dialog)
        main_dialog.open = True
        self.page.update()

    def eliminar_item(self, e):
        # Crear controles del diálogo
        input_nombre = ft.TextField(
            label="Nombre del archivo/carpeta",
            autofocus=True,
            hint_text="Ej: documento.txt",
            suffix_icon=ft.Icons.WARNING_AMBER,
            border_color=ft.Colors.ERROR
        )
        
        # 3. Funciones de manejo
        def cerrar_dialogo(e=None):
            delete_dialog.open = False
            self.page.update()
        
        def confirmar_eliminacion(e):
            nombre = input_nombre.value.strip()
            print(f"Intentando eliminar: {nombre}")  # Debug
            
            if not nombre:
                # Mostrar error en el mismo diálogo
                input_nombre.error_text = "¡Debe especificar un nombre!"
                delete_dialog.update()
                return
            
            self._animar_texto = True
            self.animar_output_texto("Eliminando")
                
            def tarea():
                try:
                    # Detectar si es archivo o carpeta
                    if "." in nombre:
                        respuesta = self.user.eliminar_archivo(nombre)
                    else:
                        respuesta = self.user.eliminar_directorio(nombre)

                    print(f"Respuesta del servidor: {respuesta}")  # Debug
                    self.output_text.value = respuesta
                    self.cargar_directorio()
                    cerrar_dialogo()

                    # Mostrar SnackBar
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"'{nombre}' eliminado", color=ft.Colors.ON_ERROR_CONTAINER),
                        bgcolor=ft.Colors.ERROR_CONTAINER,
                        duration=2000
                    )
                    self.page.snack_bar.open = True
                except Exception as ex:
                    print(f"Error al eliminar: {ex}")
                    self.output_text.value = f"Error: {str(ex)}"
                finally:
                    self._animar_texto = False
                    self.page.update()

            self.page.run_thread(tarea)

        # 4. Configurar diálogo de eliminación
        delete_dialog = ft.AlertDialog(
            title=ft.Text("Confirmar Eliminación", color=ft.Colors.ERROR),
            content=ft.Column([
                ft.Text("Esta acción no se puede deshacer", color=ft.Colors.ERROR),
                input_nombre,
                ft.Text("Ingrese el nombre exacto del elemento", size=12, color=ft.Colors.GREY)
            ], spacing=10),
            actions=[
                ft.TextButton("Cancelar",
                    style=ft.ButtonStyle(color=ft.Colors.PRIMARY),
                    on_click=cerrar_dialogo
                ),
                ft.FilledButton("Eliminar",
                    icon=ft.Icons.DELETE_FOREVER,
                    style=ft.ButtonStyle(bgcolor=ft.Colors.ERROR),
                    on_click=confirmar_eliminacion
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=10)
        )
        
        # Mostrar diálogo 
        self.page.overlay.clear()
        self.page.overlay.append(delete_dialog)
        delete_dialog.open = True
        self.page.update()

    def subir_archivo_desde_dialogo(self, e):


        def manejar_archivo_seleccionado(result):
            if not result.files:
                return
            archivo_local = result.files[0].path

            self._animar_texto = True
            self.animar_output_texto("Subiendo archivo")

            def tarea():
                try:
                    self.user.subir_archivo(archivo_local)
                    # ⚠️ Espera a que la animación se detenga
                    self._animar_texto = False
                    time.sleep(0.6)  # Asegura que la animación se apague antes de mostrar el mensaje final
                    self.output_text.value = f"✅ Archivo '{os.path.basename(archivo_local)}' subido con éxito."
                    self.cargar_directorio()
                except Exception as ex:
                    self._animar_texto = False
                    time.sleep(0.6)
                    self.output_text.value = f"❌ Error al subir: {str(ex)}"
                finally:
                    self.page.update()

            self.page.run_thread(tarea)

        file_picker = ft.FilePicker(on_result=manejar_archivo_seleccionado)
        self.page.overlay.append(file_picker)
        self.page.update()
        file_picker.pick_files(allow_multiple=False)

        

    def descargar_archivo_dialogo(self, e):
        input_nombre = ft.TextField(
            label="Nombre del archivo a descargar",
            hint_text="Ej: notas.txt",
            autofocus=True
        )

        def cerrar_dialogo(e=None):
            dialog.open = False
            self.page.update()

        def confirmar_descarga(e):
            nombre_archivo = input_nombre.value.strip()
            if not nombre_archivo:
                input_nombre.error_text = "Ingrese un nombre válido"
                dialog.update()
                return
            # Activar animación
            self._animar_texto = True
            self.animar_output_texto("Descargando archivo")

            def tarea():
                try:
                    carpeta_descargas = os.path.join(os.getcwd(), "descargas")
                    os.makedirs(carpeta_descargas, exist_ok=True)

                    destino = os.path.join(carpeta_descargas, nombre_archivo)

                    self.user.descargar_archivo(nombre_archivo, destino)
                    print('si llegaste hasta aqui significa que funciono')
                    self.output_text.value = f"✅ Archivo '{nombre_archivo}' descargado con éxito en:\n{destino}"
                    cerrar_dialogo()
                except Exception as ex:
                    self.output_text.value = f"❌ Error al descargar: {str(ex)}"
                finally:
                    self._animar_texto = False
                    self.page.update()

            self.page.run_thread(tarea)

        dialog = ft.AlertDialog(
            title=ft.Text("Descargar archivo"),
            content=input_nombre,
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar_dialogo),
                ft.FilledButton("Descargar", icon=ft.Icons.DOWNLOAD, on_click=confirmar_descarga)
            ],
            modal=True
        )

        self.page.overlay.clear()
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def construir_lista_usuarios(self, mi_usuario, usuarios_conectados, notificar_callback):
        botones = []
        for usuario in usuarios_conectados:
            if usuario != mi_usuario:
                boton = ft.ElevatedButton(
                    text=usuario,
                    on_click=lambda e, u=usuario: notificar_callback(u)
                )
                botones.append(boton)
        return ft.Column(botones)

    def notificar_usuario(self, destinatario):
        self.output_text.value = f"Notificación enviada a {destinatario}"
        self.user._enviar_mensaje(f"NOTIFY|{destinatario}|{self.nome}")
        self.page.update()
        from chat_view import ChatView
        ChatView(self.user, self.page, nome=self.nome, destinatario=destinatario).inicializar()
