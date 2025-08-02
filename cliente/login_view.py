import flet as ft
from socket_client import enviar_mensaje

def mostrar_login(page: ft.Page, guardar_usuario_callback=None):

    page.controls.clear()
    usuario = ft.TextField(label="Usuario", autofocus=True)
    clave = ft.TextField(label="Contraseña", password=True)
    mensaje = ft.Text("")

    def procesar_login(e):
        resp = enviar_mensaje(f"LOGIN|{usuario.value}|{clave.value}")
        if resp == "LOGIN_OK":
            mensaje.value = "✅ Acceso concedido"
            page.clean()
            # Importación aquí evita el ciclo
            from home_view import mostrar_home
            mostrar_home(page, usuario.value)
        else:
            mensaje.value = f"❌ {resp}"
        page.update()

    def procesar_registro(e):
        from register_view import mostrar_registro
        mostrar_registro(page)


    page.title = "MyFTP - Login"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    page.add(
        ft.Column([
            ft.Text("🔐 Bienvenido a MyFTP", size=24, weight="bold"),
            usuario,
            clave,
            ft.Row([
                ft.ElevatedButton("Iniciar sesión", on_click=procesar_login),
                ft.ElevatedButton("Registrarse", on_click=procesar_registro),
            ], alignment=ft.MainAxisAlignment.CENTER),
            mensaje
        ], width=400, alignment=ft.MainAxisAlignment.CENTER)
    )
