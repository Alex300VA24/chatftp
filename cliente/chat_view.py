import flet as ft
import os
from socket_client import enviar_mensaje, iniciar_escucha, listar_directorio, cambiar_directorio
from socket_client import descargar_archivo_de_otro_usuario, subir_archivo, ruta_actual


def mostrar_chat(page, username, destinatario=None):
    page.controls.clear()
    page.title = "Chat + Archivos"
    page.window_width = 800
    page.window_height = 600

    # ---- LISTA DE ARCHIVOS (Panel izquierdo) ----
    lista_archivos = ft.ListView(expand=True, spacing=5, padding=5, auto_scroll=False)

    def cargar_archivos():
        lista_archivos.controls.clear()
        archivos = listar_directorio(username)

        if not archivos:
            lista_archivos.controls.append(ft.Text("Directorio vacío", color=ft.Colors.GREY))
        else:
            for archivo in archivos:
                if archivo == "..":
                    # Carpeta para retroceder un nivel
                    lista_archivos.controls.append(
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.FOLDER_OPEN),
                            title=ft.Text(".."),
                            on_click=lambda e, a="..", folder=True: manejar_click_archivo(a, folder)
                        )
                    )
                    continue  # importante

                # Determinar si es carpeta o archivo
                is_folder = "." not in archivo
                icono = ft.Icons.FOLDER if is_folder else ft.Icons.INSERT_DRIVE_FILE

                lista_archivos.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(icono, size=18),
                        title=ft.Text(archivo),
                        on_click=lambda e, a=archivo, folder=is_folder: manejar_click_archivo(a, folder)
                    )
                )

        print(f'Este es ruta actual: {ruta_actual}')
        page.update()


    def manejar_click_archivo(nombre, es_carpeta):
        if es_carpeta:
            # Navegar dentro
            if cambiar_directorio(username, nombre):
                cargar_archivos()
        else:
            # Enviar archivo al chat
            destino = destino_input.value.strip()
            if not destino:
                mensajes.controls.append(ft.Text("⚠ Primero selecciona un destinatario.", color=ft.Colors.RED))
                page.update()
                return
            ruta_rel = os.path.join(*ruta_actual) if ruta_actual else "."
            print(f"[DEBUG] Enviando: FILE|{username}|{destino}|{nombre}|{ruta_rel}")
            enviar_mensaje(f"FILE|{username}|{destino}|{nombre}|{ruta_rel}")
            mensajes.controls.append(ft.Text(f"Tú enviaste '{nombre}'", color=ft.Colors.BLUE))
            page.update()

    cargar_archivos()
    panel_izquierdo = ft.Column([
        lista_archivos
    ], width=200, expand=True)

    # ---- PANEL DE CHAT (Derecha) ----
    mensajes = ft.ListView(expand=True, spacing=10, padding=10, auto_scroll=True)
    mensaje_input = ft.TextField(hint_text="Escribir un mensaje...", expand=True)
    destino_input = ft.TextField(
        label="Destinatario",
        width=200,
        value=destinatario if destinatario else ""
    )

    def enviar_click(e):
        texto = mensaje_input.value.strip()
        destino = destino_input.value.strip()
        if texto and destino:
            enviar_mensaje(f"CHAT|{username}|{destino}|{texto}")
            mensajes.controls.append(ft.Text(f"Tú: {texto}", color=ft.Colors.BLUE))
            mensaje_input.value = ""
            page.update()

    def recibir_mensaje_chat(data):
        if data.startswith("CHAT|"):
            print('Entrada al caht')
            partes = data.split("|", 3)
            if len(partes) == 4:
                origen, destino, contenido = partes[1], partes[2], partes[3]
                if destino == username:
                    mensajes.controls.append(ft.Text(f"{origen}: {contenido}", color=ft.Colors.GREEN))
                    page.update()
        elif data.startswith("FILE|"):
            try:
                print('entra al file')
                partes = data.split("|", 4)
                if len(partes) != 5:
                    print("Error: formato FILE incorrecto:", data)
                    return
                origen, destino, nombre_archivo, ruta_remota = partes[1], partes[2], partes[3], partes[4]
                print(f'Estes es origen: {origen}, este es destino{destino}')
                mensajes.controls.append(ft.Container(
                    content=ft.Column([
                        ft.Text(f"{origen} te envió: {nombre_archivo}"),
                        ft.TextButton("Descargar", on_click=lambda e: descargar_archivo_chat(origen, nombre_archivo, ruta_remota))
                    ]),
                    border=ft.Border(
                        left=ft.BorderSide(1, ft.Colors.BLACK),
                        top=ft.BorderSide(1, ft.Colors.BLACK),
                        right=ft.BorderSide(1, ft.Colors.BLACK),
                        bottom=ft.BorderSide(1, ft.Colors.BLACK)
                    ),
                    padding=5
                ))
                print('Llega al update')
                page.update()
                print('pasa update')
            except Exception as e:
                print("Error inesperado:", e)


    def descargar_archivo_chat(origen, nombre_archivo, ruta_remota):
        try:
            # Carpeta donde se guardará temporalmente el archivo
            carpeta_destino = os.path.join(os.getcwd(), "descargas_chat")
            os.makedirs(carpeta_destino, exist_ok=True)

            # Ruta de descarga local
            destino_local = os.path.join(carpeta_destino, nombre_archivo)

            # Paso 1: Descargar archivo desde el servidor del usuario origen
            # ↓↓↓ ATENCIÓN: 'origen' es el dueño original del archivo

            print(origen, nombre_archivo, ruta_remota, destino_local)
            descargar_archivo_de_otro_usuario(origen, nombre_archivo, ruta_remota, destino_local)


            # Paso 2: Subir ese archivo a tu propio servidor
            respuesta = subir_archivo(username, destino_local)
            print("⚠️ Respuesta al subir archivo:", respuesta)
            if respuesta.startswith("PUT_OK"):
                mensajes.controls.append(
                    ft.Text(f"✅ Archivo recibido de {origen} y subido a tu servidor: {nombre_archivo}", color=ft.Colors.GREY)
                )
            else:
                mensajes.controls.append(
                    ft.Text(f"⚠️ Recibido pero error al subir: {respuesta}", color=ft.Colors.ORANGE)
                )

            cargar_archivos()

        except Exception as e:
            mensajes.controls.append(
                ft.Text(f"❌ Error en descarga o subida: {e}", color=ft.Colors.RED)
            )
        finally:
            page.update()




    # ---- Botón de regresar ----
    def volver_home(e):
        destino = destino_input.value.strip()
        if destino:  # Si hay destinatario, notificamos desconexión
            enviar_mensaje(f"CHAT|{username}|{destino}|{username} se desconectó del chat.")

        from home_view import mostrar_home
        mostrar_home(page, username)

    iniciar_escucha(recibir_mensaje_chat)

    # ---- Layout general: 2 columnas ----
    layout = ft.Row([
        panel_izquierdo,
        ft.Column([
            ft.Row([
                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=volver_home),
                destino_input
            ]),
            mensajes,
            ft.Row([mensaje_input, ft.IconButton(icon=ft.Icons.SEND, on_click=enviar_click)])
        ], expand=True)
    ], expand=True)

    page.add(layout)
    page.update()
    return mensajes
