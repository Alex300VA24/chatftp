import flet as ft

class RegisterView:
    def __init__(self, page: ft.Page, cliente):
        self.page = page
        self.cliente = cliente

        self.usuario = ft.TextField(label="Nuevo usuario", autofocus=True)
        self.clave = ft.TextField(label="Nueva contraseña", password=True)
        self.mensaje = ft.Text("")

        self.page.window.prevent_close = False

    def registrar(self, e):
        username = self.usuario.value
        password = self.clave.value

        if len(username) < 5 or len(password) < 5:
            self.mensaje.value = "❌ El usuario y la contraseña deben tener al menos 5 caracteres."
            self.page.update()
            return

        resp = self.cliente._enviar_mensaje(f"REGISTER|{username}|{password}")
        if resp == "REGISTER_OK":
            self.mensaje.value = "✅ Registro exitoso. Por favor, inicia sesión."
        else:
            self.mensaje.value = f"❌ {resp}"
        self.page.update()

    def volver_login(self, e):
        from login_view2 import LoginView
        LoginView(self.page, self.cliente).mostrar()

    def mostrar(self):
        self.page.title = "MyFTP - Registro"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.controls.clear()

        self.page.add(
            ft.Column([
                ft.Text("📝 Registro de nuevo usuario", size=24, weight="bold"),
                self.usuario,
                self.clave,
                ft.Row([
                    ft.ElevatedButton("Registrar", on_click=self.registrar),
                    ft.TextButton("Volver al inicio de sesión", on_click=self.volver_login)
                ]),
                self.mensaje
            ], width=400, alignment=ft.MainAxisAlignment.CENTER)
        )
        self.page.update()
