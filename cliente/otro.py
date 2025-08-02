import flet as ft
import os
from socket_client import listar_directorio, cambiar_directorio, obtener_ruta_actual

import sys
import os

# Agrega el path del directorio raíz del proyecto (padre de 'servidor')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from servidor import auth  # ahora sí puedes importar



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



    page.update()