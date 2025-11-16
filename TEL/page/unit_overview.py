from nicegui import ui

from TEL.model import UNIT_STATUS, Unit
from TEL.database.unit import get_all_units, get_unit, quit_unit_status, update_unit
from TEL.database.mission import get_mission_by_id, get_all_mission
from TEL.page.dashboard import dashboard_page

STATUS_COLOR = {
    0: 'bg-red-500 text-white',
    1: 'bg-green-500',
    2: 'bg-gray-300',
    3: 'bg-orange-500',
    4: 'bg-yellow-500',
    5: 'bg-cyan-500',
    6: 'bg-gray-300 text-red',
    7: 'bg-gray-300',
    8: 'bg-gray-300',
    9: 'bg-gray-300',
}

def unit_stuff(unit: Unit):
    
    async def update_unit_stuff():
        unit.vf = stuff_vf.value
        unit.zf = stuff_zf.value
        unit.gf = stuff_gf.value
        unit.ms = stuff_ms.value
        unit.agt = stuff_agt.value
        await update_unit(unit)
        dashboard_page.refresh()
    
    with ui.row(align_items='center').classes('w-full justify-center'):
        with ui.card():
            stuff_vf = ui.number('Verbandsführer', min=0, step=1, value=unit.vf, on_change=update_unit_stuff).classes('w-24')
        with ui.card():
            stuff_zf = ui.number('Zugführer', min=0, step=1, value=unit.zf, on_change=update_unit_stuff).classes('w-24')
        with ui.card():
            stuff_gf = ui.number('Gruppenführer', min=0, step=1, value=unit.gf, on_change=update_unit_stuff).classes('w-24')
        with ui.card():
            stuff_ms = ui.number('Mannschaftsgrad', min=0, step=1, value=unit.ms, on_change=update_unit_stuff).classes('w-24')
        with ui.card():
            stuff_agt = ui.number('PA-Träger', min=0, step=1, value=unit.agt, on_change=update_unit_stuff).classes('w-24')

async def set_mission(unit: Unit, mission_id: int):
    unit.mission_id = mission_id
    await update_unit(unit)    
    unit_details.refresh()

async def reset_mission(unit: Unit):
    unit.mission_id = None
    await update_unit(unit)    
    unit_details.refresh()

@ui.refreshable
async def unit_overview(selected_unit):
    
    def unit_button(label: str, status: int):
        def set_label():
            selected_unit.set_text(label)
            unit_details.refresh()
        
        with ui.row(align_items='center').classes('w-full'):
            ui.label(status).classes(f'text-lg {STATUS_COLOR[status]} rounded-lg py-1 px-3')
            ui.button(text=label).classes('w-48').props('align=left').on_click(set_label)
    
    units = get_all_units()
    with ui.card():
        if not units:
            ui.label('Keine Einheit angelegt.')
        else:
            for status in [0, 5, 3, 4, 1, 2, 7, 8, 9, 6]:
                for unit in [u for u in units if u.status == status]:
                    unit_button(unit.label, unit.status)
        
@ui.refreshable
def unit_details(selected_unit: ui.label):
    
    async def reset_status():
        await quit_unit_status(selected_unit.text)
        unit_overview.refresh()
    
    unit_label = selected_unit.text
    unit = get_unit(unit_label)
    if unit:
        with ui.card(align_items='center'):
            with ui.row(align_items='center').classes('w-full justify-between'):
                ui.label().bind_text_from(selected_unit).classes('w-64 text-lg text-center font-bold')
                ui.label(UNIT_STATUS[unit.status]).classes(f'w-64 text-center text-lg {STATUS_COLOR[unit.status]} rounded-lg py-1 px-3')
                btn_quit = ui.button('Sprechwunsch quittieren', on_click=reset_status)
                btn_quit.set_enabled((unit.status == 0) or (unit.status == 5))
            
            unit_stuff(unit)
            
            mission = get_mission_by_id(unit.mission_id)
            
            if mission:
                with ui.card():
                    with ui.row(align_items='center').classes('w-full justify-between'):
                        ui.label('Einsatzstelle').classes('text-lg')
                        ui.label(f'[ {mission.label} ]')
                        ui.button('Einsatz Details', on_click=lambda: ui.navigate.to(f'/mission/{mission.id}'))
                    with ui.row(align_items='center').classes('w-full justify-center'):
                        with ui.card():
                            ui.label('Anschrift')
                            ui.label(mission.address())
                        with ui.card():
                            ui.label('Status')
                            ui.label(mission.status)
                        with ui.card():
                            ui.label('Kategorie')
                            ui.label(mission.category)
                    with ui.row(align_items='center').classes('w-full justify-center'):
                        ui.button('Vom Einsatz abziehen', on_click=lambda: reset_mission(unit))                    
                    
            else:
                all_missions = get_all_mission()
                with ui.row(align_items='center').classes('w-full justify-center'), ui.dropdown_button('Einsatzzuordnung', auto_close=True):
                    for mis in all_missions:
                        item_txt = str(mis)
                        ui.item(
                            item_txt,
                            on_click=(
                                lambda mission_id = mis.id: set_mission(unit, mission_id)
                            )
                        )
                
                      
async def unit_page() -> None:                    
        
    with ui.grid(columns='auto 2fr').classes('w-full bg-gray'):
        selected_unit = ui.label()
        selected_unit.set_visibility(False)
        await unit_overview(selected_unit=selected_unit)
        unit_details(selected_unit=selected_unit)
