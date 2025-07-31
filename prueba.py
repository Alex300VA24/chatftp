import flet as ft

def main(page: ft.Page):
    # Configuración de la ventana (nuevo estilo para Flet >= 0.26.0)
    page.title = "Prueba de Diálogo"
    page.window.width = 500
    page.window.height = 500
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Elementos de la UI
    output = ft.Text(size=16, color=ft.Colors.BLUE_800)
    input_file = ft.TextField(label="Nombre del archivo", width=300)

    # Función para manejar el diálogo
    def mostrar_dialogo(e):
        # 1. Crear contenido del diálogo
        input_nombre = ft.TextField(
            label="Nombre de la carpeta",
            autofocus=True,
            hint_text="Ej: MiCarpeta"
        )

        # 2. Funciones de callback
        def cerrar(e):
            dialog.open = False
            page.update()

        def crear(e):
            if not input_nombre.value.strip():
                input_nombre.error_text = "¡Debes ingresar un nombre!"
                dialog.update()
                return

            output.value = f"✔ Carpeta creada: '{input_nombre.value}'"
            cerrar(e)

        # 3. Crear diálogo CON todos los elementos requeridos
        dialog = ft.AlertDialog(
            title=ft.Text("Nueva carpeta"),  # Obligatorio
            content=input_nombre,             # Obligatorio
            actions=[                        # Obligatorio
                ft.TextButton("Cancelar", on_click=cerrar),
                ft.TextButton("Crear", on_click=crear),
            ],
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=10)
        )

        # 4. Mostrar diálogo (nuevo método para Flet >= 0.26.0)
        page.overlay.clear()  # Limpiar diálogos anteriores
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # Botón principal
    btn_crear = ft.ElevatedButton(
        "Mostrar diálogo",
        icon=ft.Icons.CREATE_NEW_FOLDER,
        on_click=mostrar_dialogo
    )

    # Diseño de la página
    page.add(
        ft.Column(
            [
                ft.Icon(ft.Icons.FOLDER, size=50),
                ft.Text("Administrador de archivos", size=24, weight=ft.FontWeight.BOLD),
                btn_crear,
                output
            ],
            spacing=25,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

# Ejecutar la app
ft.app(target=main)