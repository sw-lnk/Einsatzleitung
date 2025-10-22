import os
from nicegui import ui

def index_page() -> None:
    with ui.row().classes('w-full justify-center'), ui.card(align_items='center'):
        ui.image(os.path.join('TEL', 'data', 'logo_TEL.png')).classes('w-64 m-0 p-0')
        ui.label('Digitale Unterstützung in der Technische Einsatzleitung').classes('text-center')
            