from nicegui import ui

from TEL.page.utils import unit_details, unit_overview

async def unit_page() -> None:                    
        
    with ui.grid(columns='auto 2fr').classes('w-full bg-gray'):
        selected_unit = ui.label()
        selected_unit.set_visibility(False)
        await unit_overview(selected_unit)
        unit_details(selected_unit)
