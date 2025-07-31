chatftp/
│
├── servidor/
│   ├── server.py          ← Lógica del servidor principal
│   ├── auth.py            ← Registro/login con SQLite
│   ├── handlers/          ← Carpeta para modular los comandos
│
├── cliente/
│   ├── main.py            ← Arranque de la interfaz Flet
│   ├── login_view.py      ← Pantalla de login y registro
│   ├── home_view.py       ← Interfaz tipo "explorador" (imagen 1)
│   ├── chat_view.py       ← Interfaz de chat (imagen 2)
│   ├── socket_client.py   ← Módulo para manejo del socket UDP
│   ├── archivos/          ← Carpeta donde se guardan archivos del cliente
│
├── base_datos/
│   └── usuarios.db        ← Archivo de base de datos (SQLite)
