import flet as ft
from home_view import HomeView

class LoginView:
    def __init__(self, page: ft.Page, user):
        self.page = page
        self.cliente = user

        self.usuario = ft.TextField(label="Usuario", autofocus=True)
        self.clave = ft.TextField(label="Contraseña", password=True)
        self.mensaje = ft.Text("")

        self.page.window.prevent_close = False

    def procesar_login(self, e):
        nome_usuario = self.usuario.value
        password = self.clave.value
        self.cliente.login(nome_usuario)
        resp = self.cliente._enviar_mensaje(f"LOGIN|{nome_usuario}|{password}")

        if resp == "LOGIN_OK":
            self.mensaje.value = "✅ Acceso concedido"
            self.page.clean()
            HomeView(self.page, self.cliente, self.usuario.value).mostrar()
        else:
            self.mensaje.value = f"❌ {resp}"
        self.page.update()

    def procesar_registro(self, e):
        from register_view import RegisterView
        RegisterView(self.page, self.cliente).mostrar()

    def mostrar(self):
        self.page.title = "MyFTP - Login"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER

        self.page.controls.clear()
        self.page.add(
            ft.Column([
                ft.Text("🔐 Bienvenido a MyFTP", size=24, weight="bold"),
                self.usuario,
                self.clave,
                ft.Row([
                    ft.ElevatedButton("Iniciar sesión", on_click=self.procesar_login),
                    ft.ElevatedButton("Registrarse", on_click=self.procesar_registro),
                ], alignment=ft.MainAxisAlignment.CENTER),
                self.mensaje
            ], width=400, alignment=ft.MainAxisAlignment.CENTER)
        )
        self.page.update()
