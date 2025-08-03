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

    def animar_mensaje_login(self, base="Procesando"):
        import threading, time

        def animar():
            puntos = [".", "..", "..."]
            relojes = ["🕛", "🕐", "🕑"]
            i = 0
            while self._animar_texto:
                self.mensaje.value = f"{base} {puntos[i % 3]} {relojes[i % 3]}"
                self.page.update()
                time.sleep(0.5)
                i += 1

        threading.Thread(target=animar, daemon=True).start()


    def procesar_login(self, e):
        nome_usuario = self.usuario.value.strip()
        password = self.clave.value.strip()

        if not nome_usuario or not password:
            self.mensaje.value = "⚠️ Usuario y contraseña requeridos"
            self.page.update()
            return

        self._animar_texto = True
        self.animar_mensaje_login("Iniciando sesión")

        def tarea():
            try:
                self.cliente.login(nome_usuario)
                resp = self.cliente._enviar_mensaje(f"LOGIN|{nome_usuario}|{password}")

                if resp == "LOGIN_OK":
                    self._animar_texto = False
                    self.mensaje.value = "✅ Acceso concedido"
                    self.page.clean()
                    HomeView(self.page, self.cliente, self.usuario.value).mostrar()
                else:
                    self._animar_texto = False
                    self.mensaje.value = f"❌ {resp}"

                self.page.update()
            except Exception as ex:
                self._animar_texto = False
                self.mensaje.value = f"❌ Error: {str(ex)}"
                self.page.update()

        self.page.run_thread(tarea)


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
