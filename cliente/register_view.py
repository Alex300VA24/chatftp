import flet as ft
import threading,time

class RegisterView:
    def __init__(self, page: ft.Page, cliente):
        self.page = page
        self.cliente = cliente

        self.usuario = ft.TextField(label="Nuevo usuario", autofocus=True)
        self.clave = ft.TextField(label="Nueva contraseña", password=True)
        self.mensaje = ft.Text("")

        self.page.window.prevent_close = False


    # Dentro de RegisterView

    def animar_mensaje_registro(self, mensaje_base):
        relojes = ["🕛", "🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙", "🕚"]
        puntos = ["", ".", "..", "..."]
        i = 0
        j = 0
        while getattr(self, "_animar_texto", False):
            texto = f"{mensaje_base} {puntos[i % len(puntos)]} {relojes[j % len(relojes)]}"
            self.mensaje.value = texto
            self.page.update()
            time.sleep(0.4)
            i += 1
            j += 1


    def registrar(self, e):
        username = self.usuario.value
        password = self.clave.value

        if len(username) < 5 or len(password) < 5:
            self.mensaje.value = "❌ El usuario y la contraseña deben tener al menos 5 caracteres."
            self.page.update()
            return

        self._animar_texto = True
        threading.Thread(target=self.animar_mensaje_registro, args=("Registrando usuario",), daemon=True).start()

        def tarea():
            try:
                resp = self.cliente._enviar_mensaje(f"REGISTER|{username}|{password}")
                self._animar_texto = False
                time.sleep(0.3)  # Para que la animación pare antes de mostrar resultado
                if resp == "REGISTER_OK":
                    self.mensaje.value = "✅ Registro exitoso. Por favor, inicia sesión."
                else:
                    self.mensaje.value = f"❌ {resp}"
                self.page.update()
            except Exception as ex:
                self._animar_texto = False
                self.mensaje.value = f"❌ Error: {str(ex)}"
                self.page.update()

        threading.Thread(target=tarea, daemon=True).start()

    def volver_login(self, e):
        from login_view import LoginView
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
