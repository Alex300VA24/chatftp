import flet as ft
from socket_client import enviar_mensaje, iniciar_escucha

def mostrar_chat(page, username):
    mensajes = ft.ListView(expand=True, spacing=10, padding=10, auto_scroll=True)
    mensaje_input = ft.TextField(hint_text="Escribe tu mensaje", expand=True)
    destino_input = ft.TextField(label="Destinatario", width=200)

    def enviar_click(e):
        texto = mensaje_input.value.strip()
        destino = destino_input.value.strip()
        if texto and destino:
            enviar_mensaje(f"CHAT|{destino}|{texto}")
            mensajes.controls.append(ft.Text(f"Tú a {destino}: {texto}", color=ft.Colors.BLUE))
            mensaje_input.value = ""
            page.update()

    def recibir_mensaje(data):
        if data.startswith("CHAT|"):
            partes = data.split("|", 2)
            if len(partes) == 3:
                origen, contenido = partes[1], partes[2]
                mensajes.controls.append(ft.Text(f"{origen}: {contenido}", color=ft.Colors.GREEN))
                page.update()

    iniciar_escucha(recibir_mensaje)

    page.controls.clear()
    page.add(
        ft.Column([
            ft.Text("Chat privado", size=20, weight=ft.FontWeight.BOLD),
            destino_input,
            mensajes,
            ft.Row([mensaje_input, ft.IconButton(icon=ft.Icons.SEND, on_click=enviar_click)])
        ], expand=True)
    )
    page.update()

