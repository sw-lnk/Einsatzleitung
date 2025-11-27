from nicegui import ui, app

from TEL.model import Unit, UNIT_STATUS, Message, Priority, Status
from TEL.authentication import get_current_user
from TEL.database.mission import get_mission_units, get_mission_by_id, get_all_mission
from TEL.database.unit import get_unit, get_all_units, quit_unit_status, update_unit
from TEL.database.message import create_message
from TEL.page.dashboard import dashboard_page
from TEL.page.utils import STATUS_COLOR

async def create_unit_message(content: str, mission_id:int) -> Message:
    user = await get_current_user(app.storage.user.get('token'))
    message = Message(
        prio=Priority.low,
        content=content,
        user_id=user.id,
        mission_id=mission_id
    )
    await create_message(message)
    return message


async def send_status(unit: Unit, status_id: int):
        unit.status = status_id        
        
        if status_id in [1, 2]:
            if unit.mission_id:
                await create_unit_message(f'{unit.label} mit Status {status_id} aus Einsatz entlassen.', unit.mission_id)
            unit.mission_id = None
        elif status_id == 3 and unit.mission_id:
            await create_unit_message(f'{unit.label} Einsatz übernommen (Status 3).', unit.mission_id)
        elif status_id == 4 and unit.mission_id:
            await create_unit_message(f'{unit.label} Einsatzstelle an (Status 4).', unit.mission_id)
        elif status_id == 7 and unit.mission_id:
            await create_unit_message(f'{unit.label} Patient aufgenommen: Status 7.', unit.mission_id)
        elif status_id == 8 and unit.mission_id:
            await create_unit_message(f'{unit.label} am Transportziel: Status 8.', unit.mission_id)
        elif status_id == 9 and unit.mission_id:
            await create_unit_message(f'{unit.label} Notarzt aufgenommen: Status 9.', unit.mission_id)
            
        await update_unit(unit)
        unit_details.refresh()
        unit_overview.refresh()
        mission_units.refresh()
        status_tableau.refresh()


@ui.refreshable
async def status_tableau(unit_label: str):
    unit = get_unit(unit_label)
    mission = get_mission_by_id(unit.mission_id)
    with ui.row().classes('w-full justify-center'), ui.card(align_items='center'):
        ui.label(unit.label).classes('text-xl')
        ui.label(str(mission) if mission else '###')
        for status_id, status_text in UNIT_STATUS.items():
            color_btn = 'secondary' if status_id == unit.status else 'primary'
            ui.button(
                f'{status_id} - {status_text}',
                color=color_btn,
                ).classes('w-full').props('align=left').on_click(lambda status_id_=status_id, unit_=unit: send_status(unit_, status_id_))


async def reset_status(unit_label: str):
    await quit_unit_status(unit_label)
    mission_units.refresh()
    status_tableau.refresh()
    unit_overview.refresh()


@ui.refreshable
def mission_units(mission_id: int, input_ui: ui.input):
    units = get_mission_units(mission_id)
    unit_strength = {
        'vf': sum([unit.vf for unit in units]),
        'zf': sum([unit.zf for unit in units]),
        'gf': sum([unit.gf for unit in units]),
        'ms': sum([unit.ms for unit in units]),
        'agt': sum([unit.agt for unit in units]),
    }
    unit_strength['total'] = sum([unit_strength.get('vf'), unit_strength.get('zf'), unit_strength.get('gf'), unit_strength.get('ms')])
    if units is None:
        ui.label('Keine Einheit zugeordnet.')
        return
    with ui.card(align_items='center').classes('w-full'):
        with ui.row(align_items='center').classes('w-full justify-center'):
            ui.label(unit_strength.get('vf'))
            ui.label('/')
            ui.label(unit_strength.get('zf'))
            ui.label('/')
            ui.label(unit_strength.get('gf'))
            ui.label('/')
            ui.label(unit_strength.get('ms'))
            ui.label('/')
            ui.label(unit_strength.get('total')).classes('underline')
            ui.label(f'[ {unit_strength.get('ms')} ]')
            
        for status in [0, 5, 3, 4, 1, 2, 7, 8, 9, 6]:
            for unit in units:
                if unit.status == status:
                    with ui.row(align_items='center').classes('w-full'):
                        ui.label(unit.status).classes(f'text-lg {STATUS_COLOR[unit.status]} rounded-lg py-1 px-3')
                        ui.button(text=unit.label).classes('w-48').props('align=left').on_click(
                            lambda label=unit.label: input_ui.set_value(f'{label}: ')
                        )
                        if unit.status in [0, 5]:
                            ui.button(icon='o_check_box').on_click(
                                lambda label=unit.label: reset_status(label)
                            )


async def set_mission(unit: Unit, mission_id: int):
    message = await create_unit_message(f'{unit.label} Einsatz zugeordnet.', mission_id)
    await create_message(message)
    
    unit.mission_id = mission_id
    await update_unit(unit) 
    unit_details.refresh()    
    mission_units.refresh()

async def reset_mission(unit: Unit):
    message = await create_unit_message(f'{unit.label} vom Einsatz abgezogen.', unit.mission_id)
    await create_message(message)
    
    unit.mission_id = None
    await update_unit(unit) 
    unit_details.refresh()    
    mission_units.refresh()
    

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


@ui.refreshable
def unit_details(selected_unit: ui.label):
    
    unit_label = selected_unit.text
    unit = get_unit(unit_label)
    if unit:
        with ui.card(align_items='center'):
            with ui.row(align_items='center').classes('w-full justify-between'):
                ui.label().bind_text_from(selected_unit).classes('w-64 text-lg text-center font-bold')
                ui.label(UNIT_STATUS[unit.status]).classes(f'w-64 text-center text-lg {STATUS_COLOR[unit.status]} rounded-lg py-1 px-3')
                btn_quit = ui.button('Sprechwunsch quittieren', on_click= lambda: reset_status(unit_label))
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
                        if mis.status not in [Status.new, Status.in_progress]:
                            continue
                        item_txt = str(mis)
                        ui.item(
                            item_txt,
                            on_click=(
                                lambda mission_id = mis.id: set_mission(unit, mission_id)
                            )
                        )


@ui.refreshable
async def unit_overview(selected_unit: ui.label):
    
    def unit_button(unit_label: str, status: int):
        def set_label():
            selected_unit.set_text(unit_label)
            unit_details.refresh()
        
        with ui.row(align_items='center').classes('w-full'):
            ui.label(status).classes(f'text-lg {STATUS_COLOR[status]} rounded-lg py-1 px-3')
            ui.button(text=unit_label).classes('w-48').props('align=left').on_click(set_label)
    
    units = get_all_units()
    with ui.card():
        if not units:
            ui.label('Keine Einheit angelegt.')
        else:
            for status in [0, 5, 3, 4, 1, 2, 7, 8, 9, 6]:
                for unit in [u for u in units if u.status == status]:
                    unit_button(unit.label, unit.status)
