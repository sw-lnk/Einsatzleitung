import traceback
from nicegui import ui, app
from fastapi.exceptions import HTTPException

from TEL.page import theme

# =============================================================================
# EXCEPTION PAGES
# =============================================================================

def exception_message(message: str, icon: str = 'error') -> None:
    with theme.frame(''):
        with ui.column().classes('absolute-center items-center gap-8'):
            ui.icon(icon, size='xl')
            ui.label(message).classes('text-2xl')
            

@app.on_page_exception
def exception_page(exception: Exception) -> None:
    if isinstance(exception, HTTPException):
        if exception.status_code == 401:
            ui.navigate.to('/login')
            return
        if exception.status_code == 403:
            exception_message('Fehlende Berechtigung', 'lock')
            return
    
    with theme.frame(''):
        with ui.column().classes('absolute-center items-center gap-8'):
            ui.icon('error', size='xl')
            ui.label(f'{exception}').classes('text-2xl')
            ui.code(traceback.format_exc(chain=False))
