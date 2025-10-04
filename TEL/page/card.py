from nicegui import ui

def card(content: str, comment: str = None, icon: str = 'info', color: str = 'gray-300'):
    with ui.card().classes(f'bg-{color} w-full'):        
        with ui.row(align_items='center'):
            ui.icon(icon, size='xs')
            ui.label(comment).classes('text-xs')
        ui.label(content).classes('text-xl')