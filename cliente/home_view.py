import flet as ft
import os
import socket_client
from socket_client import enviar_mensaje, listar_directorio, cambiar_directorio, obtener_ruta_actual
from socket_client import crear_directorio, eliminar_directorio, eliminar_archivo, subir_archivo, descargar_archivo
from socket_client import procesar_notify, iniciar_escucha
from chat_view import mostrar_chat
import sys
import os

# Agrega el path del directorio raíz del proyecto (padre de 'servidor')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from servidor import auth  # ahora sí puedes importar



def mostrar_home(page, username):


    def recibir_mensaje_home(mensaje: str):
        print('Recibio mensaje del servidor')
        if mensaje.startswith("NOTIFY|"):
            print('Dio verdadero al mensaje')
            remitente = procesar_notify(mensaje, username)
            if remitente:
                mostrar_dialogo_notify(page, remitente)


    def mostrar_dialogo_notify(page, remitente: str):
        print('Llega a mostrar dialogo notify')

        dialogo = None  # Declaramos la variable para que esté en el scope

        def cerrar_dialogo(e=None):
            nonlocal dialogo
            if dialogo:
                dialogo.open = False
                page.update()

        def aceptar_chat(e=None):
            nonlocal dialogo
            if dialogo:
                dialogo.open = False
                print("Aceptar presionado")
                page.update()
                from chat_view import mostrar_chat
                from socket_client import enviar_mensaje

                # Abrir el chat y obtener el ListView de mensajes
                mensajes = mostrar_chat(page, username=username, destinatario=remitente)

                # Enviar mensaje automático de conexión
                if remitente:
                    mensaje_conexion = "Está conectado al chat"
                    # Nuevo protocolo: remitente | destinatario | mensaje
                    enviar_mensaje(f"CHAT|{username}|{remitente}|{mensaje_conexion}")

                    # Mostrarlo en tu pantalla como si lo recibieras del otro usuario (verde)
                    mensajes.controls.append(
                        ft.Text(f"{remitente}: {mensaje_conexion}", color=ft.Colors.GREEN)
                    )
                    page.update()

        print("Construyendo título...")
        titulo = ft.Text("Solicitud de chat privado", weight=ft.FontWeight.BOLD)
        print("Construyendo contenido...")
        contenido = ft.Text(f"{remitente} quiere hablar contigo.")
        print("Construyendo botones...")
        btn_cerrar = ft.TextButton("Cerrar", style=ft.ButtonStyle(color=ft.Colors.ERROR), on_click=cerrar_dialogo)
        btn_aceptar = ft.FilledButton("Aceptar", icon=ft.Icons.CHAT, on_click=aceptar_chat)
        print("Creando AlertDialog...")
        dialogo = ft.AlertDialog(
            title=titulo,
            content=contenido,
            actions=[btn_cerrar, btn_aceptar],
            actions_alignment=ft.MainAxisAlignment.END,
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=10)
        )
        print("AlertDialog creado")

        try:
            page.overlay.clear()
            page.overlay.append(dialogo)
            dialogo.open = True
            page.update()
            print('se actualizo')
        except Exception as e:
            print(f"[ERROR MOSTRAR DIALOGO] {e}")


    print(f"[DEBUG] Registrando listener de {username}")
    iniciar_escucha(recibir_mensaje_home)



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
        page.controls.clear()
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

    def subir_archivo_desde_dialogo(e):
        def manejar_archivo_seleccionado(result):
            if not result.files:
                return
            archivo_local = result.files[0].path
            try:
                output_text.value = "Subiendo archivo..."
                subir_archivo(username, archivo_local)
                output_text.value = f"Archivo '{archivo_local}' subido con éxito."
                cargar_directorio()
                page.update()
            except Exception as ex:
                output_text.value = f"Error al subir: {str(ex)}"
                page.update()

        file_picker = ft.FilePicker(on_result=manejar_archivo_seleccionado)
        page.overlay.append(file_picker)
        page.update()  # 🔁 Esto sincroniza el control con la página antes de usarlo

        file_picker.pick_files(allow_multiple=False)

    
    def descargar_archivo_dialogo(e):
        input_nombre = ft.TextField(
            label="Nombre del archivo a descargar",
            hint_text="Ej: notas.txt",
            autofocus=True
        )

        def cerrar_dialogo(e=None):
            dialog.open = False
            page.update()

        def confirmar_descarga(e):
            nombre_archivo = input_nombre.value.strip()
            if not nombre_archivo:
                input_nombre.error_text = "Ingrese un nombre válido"
                dialog.update()
                return
            try:
                output_text.value = "Descargando archivo..."
                # Carpeta "descargas" en la misma raíz del script
                carpeta_descargas = os.path.join(os.getcwd(), "descargas")
                os.makedirs(carpeta_descargas, exist_ok=True)  # Crea la carpeta si no existe

                destino = os.path.join(carpeta_descargas, nombre_archivo)

                descargar_archivo(username, nombre_archivo, destino)
                print('si llegaste hasta aqui significa que funciono')
                output_text.value = f"Archivo '{nombre_archivo}' descargado con éxito en: {destino}"
                cerrar_dialogo()
                page.update()

            except Exception as ex:
                output_text.value = f"Error al descargar: {str(ex)}"
                page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Descargar archivo"),
            content=input_nombre,
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar_dialogo),
                ft.FilledButton("Descargar", icon=ft.Icons.DOWNLOAD, on_click=confirmar_descarga)
            ],
            modal=True
        )

        page.overlay.clear()
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def construir_lista_usuarios(mi_usuario, usuarios_conectados, notificar_callback):
        botones = []
        for usuario in usuarios_conectados:
            if usuario != mi_usuario:
                boton = ft.ElevatedButton(
                    text=usuario,
                    on_click=lambda e, u=usuario: notificar_callback(u)
                )
                botones.append(boton)
        return ft.Column(botones)
    
    def notificar_usuario(destinatario):
        output_text.value = f"Notificación enviada a {destinatario}"
        enviar_mensaje(f"NOTIFY|{destinatario}|{username}")  # NUEVO COMANDO
        page.update()
        from chat_view import mostrar_chat
        mostrar_chat(page, username=username, destinatario=destinatario)


    usuarios_activos = auth.obtener_usuarios_activos()

    lista_usuarios = construir_lista_usuarios(username, usuarios_activos, notificar_usuario)

    
    def abrir_archivo(e):
        output_text.value = "Selecciona un archivo"
        page.update()


    # Botones superiores en la barra de herramientas
    # Botones superiores en la barra de herramientas
    barra_herramientas = ft.Row([
        ft.IconButton(icon=ft.Icons.CREATE_NEW_FOLDER, tooltip="Crear carpeta", on_click=crear_carpeta),
        ft.IconButton(icon=ft.Icons.FOLDER_OPEN, tooltip="Abrir archivo", on_click=abrir_archivo),
        ft.IconButton(icon=ft.Icons.DELETE, tooltip="Eliminar", on_click=eliminar_item),
        ft.IconButton(icon=ft.Icons.UPLOAD_FILE, tooltip="Subir archivo", on_click=subir_archivo_desde_dialogo),
        ft.IconButton(icon=ft.Icons.DOWNLOAD, tooltip="Descargar archivo", on_click=descargar_archivo_dialogo)  # <-- NUEVO
    ], alignment=ft.MainAxisAlignment.START)


    # Panel derecho con contenido principal
    panel_contenido = ft.Column([
        barra_herramientas,
        ruta_label,
        lista_directorio,
        ft.Divider(),
        output_text
    ], expand=True)

    # Estructura general de la app
    layout = ft.Row([
        ft.Container(content=lista_usuarios, padding=10, width=150, bgcolor=ft.Colors.GREY_200),
        ft.VerticalDivider(width=1),
        ft.Container(content=panel_contenido, padding=10, expand=True)
    ], expand=True)

    # Limpiar y añadir layout principal
    page.controls.clear()
    page.add(layout, ft.Button("Abrir chat", on_click=abrir_chat), ft.Button("Cerrar Session", on_click=logout))
    cargar_directorio()


    page.update()

    

