import flet as ft
from socket_client import enviar_mensaje, listar_directorio, cambiar_directorio, obtener_ruta_actual
from socket_client import crear_directorio, eliminar_directorio, eliminar_archivo
from chat_view import mostrar_chat


def mostrar_home(page, username):
    page.title = "MyFTP - Panel Principal"
    page.window_width = 600
    page.window_height = 600
    page.scroll = ft.ScrollMode.AUTO

    output_text = ft.Text("", size=14)
    ruta_label = ft.Text("", size=13, italic=True, color=ft.Colors.BLUE_GREY)
    input_box = ft.TextField(label="Comando FTP", width=400)
    lista_directorio = ft.Column(spacing=5)
    processing = False


    # Cargar archivos/carpetas del directorio actual
    def cargar_directorio():
        lista_directorio.controls.clear()
        items = listar_directorio(username)

        if not items:
            lista_directorio.controls.append(
                ft.Text("Directorio vacío", color=ft.Colors.GREY_400)
            )
        else:
            for item in items:
                # Elemento para navegar hacia atrás (..)
                if item == "..":
                    lista_directorio.controls.append(
                        ft.ListTile(
                            title=ft.Text(".."),
                            leading=ft.Icon(ft.Icons.FOLDER_OPEN),
                            on_click=lambda e, x="..": navegar(x)
                        )
                    )
                    continue

                # Determinar icono según tipo (carpeta/archivo)
                is_folder = "." not in item
                icono = ft.Icons.FOLDER if is_folder else ft.Icons.INSERT_DRIVE_FILE
                color_icono = ft.Colors.AMBER_300 if is_folder else ft.Colors.BLUE_300

                # Crear elemento de lista con cierre sobre el nombre
                lista_directorio.controls.append(
                    ft.ListTile(
                        title=ft.Text(
                            item,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            tooltip=item if len(item) > 20 else None
                        ),
                        leading=ft.Icon(icono, color=color_icono),
                        on_click=lambda e, x=item: navegar(x),  # Captura correcta del valor
                        dense=True,
                        hover_color=ft.Colors.with_opacity(0.1, ft.Colors.PRIMARY)
                    )
                )

        # Actualizar UI
        ruta_label.value = f"📂 Ruta: {obtener_ruta_actual()}"
        page.update()


    def navegar(nombre):
        nonlocal processing
        if processing:
            return
        processing = True

        try:
            if nombre == "..":
                if cambiar_directorio(username, ".."):
                    output_text.value = f"Subiste un nivel."
                    cargar_directorio()
                else:
                    output_text.value = "Ya estás en la carpeta raíz."
            elif "." not in nombre:
                if cambiar_directorio(username, nombre):
                    output_text.value = f"Entraste a '{nombre}'"
                    cargar_directorio()
                else:
                    output_text.value = f"Error al entrar a '{nombre}'"
            else:
                output_text.value = f"'{nombre}' es un archivo."
            page.update()
        finally:
            processing = False  # siempre se libera, incluso si falla




    def ejecutar_comando(e):
        comando = input_box.value.strip()
        if not comando:
            return
        respuesta = enviar_mensaje(comando)
        output_text.value = respuesta
        cargar_directorio()  # Para reflejar cambios como mkdir/rmdir
        page.update()

    def abrir_chat(e):
        mostrar_chat(page, username)

    lista_archivos = ft.Text("")  # Mostrar archivos
    
    def logout(e):
        enviar_mensaje(f"LOGOUT|{username}")
        from login_view import mostrar_login 
        mostrar_login(page)

 
    def crear_carpeta(e):
        # 1. Configuración inicial
        print(f'Botón presionado - Página válida: {page is not None}')
        
        # 2. Crear controles del diálogo
        input_nombre = ft.TextField(
            label="Nombre de la carpeta",
            autofocus=True,
            hint_text="Ej: MiProyecto",
            capitalization=ft.TextCapitalization.WORDS,
            border_color=ft.Colors.PRIMARY
        )
        
        # 3. Funciones de manejo
        def cerrar_dialogo(e=None):
            main_dialog.open = False
            page.update()
        
        def confirmar_creacion(e):
            nombre = input_nombre.value.strip()
            print(f'Intento de creación: "{nombre}"')
            
            if not nombre:
                # Mostrar diálogo de error
                error_dialog = ft.AlertDialog(
                    title=ft.Text("Error", color=ft.Colors.ERROR),
                    content=ft.Text("Debe ingresar un nombre válido"),
                    actions=[
                        ft.TextButton("Entendido", on_click=lambda e: (setattr(error_dialog, 'open', False), page.update()))
                    ],
                    shape=ft.RoundedRectangleBorder(radius=8)
                )
                page.overlay.append(error_dialog)
                error_dialog.open = True
                page.update()
                return
                
            try:
                # Ejecutar comando FTP
                crear_directorio(username, nombre)
                respuesta = f"Carpeta '{nombre}' creada correctamente."
                print(f"Respuesta del servidor: {respuesta}")
                
                # Actualizar interfaz
                output_text.value = respuesta
                cargar_directorio()
                cerrar_dialogo()
                
                # Mostrar notificación de éxito
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Carpeta '{nombre}' creada", color=ft.Colors.ON_PRIMARY),
                    bgcolor=ft.Colors.PRIMARY
                )
                page.snack_bar.open = True
                page.update()
                
            except Exception as ex:
                print(f"Error al crear carpeta: {ex}")
                output_text.value = f"Error: {str(ex)}"
                page.update()

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
        page.overlay.clear()
        page.overlay.append(main_dialog)
        main_dialog.open = True
        page.update()


    def eliminar_item(e):
        # 1. Configuración inicial
        print("Iniciando proceso de eliminación")  # Debug
        
        # 2. Crear controles del diálogo
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
            page.update()
        
        def confirmar_eliminacion(e):
            nombre = input_nombre.value.strip()
            print(f"Intentando eliminar: {nombre}")  # Debug
            
            if not nombre:
                # Mostrar error en el mismo diálogo
                input_nombre.error_text = "¡Debe especificar un nombre!"
                delete_dialog.update()
                return
                
            try:
                # Detectar si es archivo o carpeta según extensión (sólo por convención)
                if "." in nombre:
                    respuesta = eliminar_archivo(username, nombre)
                else:
                    respuesta = eliminar_directorio(username, nombre)

                print(f"Respuesta del servidor: {respuesta}")  # Debug

                output_text.value = respuesta
                cargar_directorio()
                cerrar_dialogo()

                # Mostrar confirmación
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"'{nombre}' eliminado", color=ft.Colors.ON_ERROR_CONTAINER),
                    bgcolor=ft.Colors.ERROR_CONTAINER,
                    duration=2000
                )
                page.snack_bar.open = True
                page.update()
                
            except Exception as ex:
                print(f"Error al eliminar: {ex}")  # Debug
                output_text.value = f"Error: {str(ex)}"
                page.update()

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
        
        # 5. Mostrar diálogo (nuevo método Flet >= 0.26.0)
        page.overlay.clear()
        page.overlay.append(delete_dialog)
        delete_dialog.open = True
        page.update()


    btn_chat = ft.ElevatedButton("Abrir chat", on_click=abrir_chat)
    btn_logout = ft.ElevatedButton("Cerrar sesión", on_click=logout)
    ejecutar_btn = ft.ElevatedButton("Ejecutar comando", on_click=ejecutar_comando)
    ejecutar_mkdir = ft.ElevatedButton("Crear carpeta", on_click=crear_carpeta)
    ejecutar_eliminado = ft.ElevatedButton("Eliminar archivo/carpeta", on_click=eliminar_item)
    comandos_utiles = ft.Text("Comandos disponibles: ls, cd, cd.., mkdir, rmdir, put, get", italic=True, size=12, color=ft.Colors.GREY)

    # Interfaz completa
    page.controls.clear()
    page.add(
        ft.Column([
            ft.Text(f"Bienvenido, {username}!", size=22, weight=ft.FontWeight.BOLD),
            comandos_utiles,
            ft.Row([input_box, ejecutar_btn]),
            output_text,
            ft.Divider(),
            ft.Text("Explorador de archivos:", size=16, weight=ft.FontWeight.W_600),
            ruta_label,
            lista_directorio,
            ft.Divider(),
            ft.Row([
                ejecutar_mkdir,
                ejecutar_eliminado
            ]),
            ft.Row([btn_chat, btn_logout])
        ], spacing=20, expand=True)
    )

    cargar_directorio()
    page.update()
