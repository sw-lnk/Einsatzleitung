from nicegui import ui       

def dashboard_page() -> None:
    with ui.row(align_items='stretch').classes('w-full justify-center'):
        ui.label('Dashboard').classes('text-xl')
        