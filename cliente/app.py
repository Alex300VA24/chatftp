import flet as ft
from login_view import LoginView
from client_chatftp import ChatFTPClient  # tu clase de comunicación UDP

SERVER_IP = "192.168.3.38"
#SERVER_IP = "172.30.17.209"
#SERVER_IP = "172.30.12.61"
SERVER_PORT = 2121

def main(page: ft.Page):
    page.window_width = 500
    page.window_height = 400

    cliente = ChatFTPClient(SERVER_IP, SERVER_PORT)  # creas la instancia del cliente UDP
    LoginView(page, cliente).mostrar()   # pasas page y cliente a tu vista

ft.app(target=main)
