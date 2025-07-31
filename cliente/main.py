import flet as ft
from login_view import mostrar_login

def main(page: ft.Page):
    page.window_width = 500
    page.window_height = 400
    mostrar_login(page)

ft.app(target=main)
