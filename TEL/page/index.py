import os
from nicegui import ui

def index_page() -> None:
    with ui.row().classes('w-full justify-center'):
        ui.label(os.getenv('APP_TITLE')).classes('text-2xl border-2 border-current rounded p-2')
            