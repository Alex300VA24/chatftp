import flet as ft
from socket_client import enviar_mensaje

def mostrar_registro(page: ft.Page):
    usuario = ft.TextField(label="Nuevo usuario", autofocus=True)
    clave = ft.TextField(label="Nueva contraseña", password=True)
    mensaje = ft.Text("")

    def registrar(e):
        resp = enviar_mensaje(f"REGISTER|{usuario.value}|{clave.value}")
        if resp == "REGISTER_OK":
            mensaje.value = "✅ Registro exitoso. Por favor, inicia sesión."
            page.update()
            from login_view import mostrar_login
            mostrar_login(page)
        else:
            mensaje.value = f"❌ {resp}"
            page.update()

    def volver_login(e):
        from login_view import mostrar_login
        mostrar_login(page)

    page.title = "MyFTP - Registro"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.controls.clear()
    page.add(
        ft.Column([
            ft.Text("📝 Registro de nuevo usuario", size=24, weight="bold"),
            usuario,
            clave,
            ft.Row([
                ft.ElevatedButton("Registrar", on_click=registrar),
                ft.TextButton("Volver al inicio de sesión", on_click=volver_login)
            ]),
            mensaje
        ], width=400, alignment=ft.MainAxisAlignment.CENTER)
    )
    page.update()
