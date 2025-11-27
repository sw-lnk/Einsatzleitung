from nicegui import ui, app
from fastapi import HTTPException, status

from TEL.model import UNIT_STATUS, Permission, Unit, Message, Priority
from TEL.database.unit import get_unit, update_unit_status, update_unit
from TEL.database.mission import get_mission_by_id
from TEL.database.message import create_message
from TEL.authentication import get_current_user
from TEL.page import unit_overview
from TEL.page.mission_detail import mission_units
from TEL.page.mission_detail import messages, mission_messages
from TEL.page.unit_overview import unit_details

async def create_unit_message(content: str, mission_id:int) -> Message:
    user = await get_current_user(app.storage.user.get('token'))
    message = Message(
        prio=Priority.low,
        content=content,
        user_id=user.id,
        mission_id=mission_id
    )
    await create_message(message)
    messages.insert(0, message)
    mission_messages.refresh()
    return message

async def unit_status(unit_label: str):
    
    @ui.refreshable
    async def status_tableau(unit: Unit):
        mission = get_mission_by_id(unit.mission_id)
        with ui.row().classes('w-full justify-center'), ui.card(align_items='center'):
            ui.label(unit.label).classes('text-xl')
            ui.label(str(mission) if mission else '###')
            for status_id, status_text in UNIT_STATUS.items():
                color_btn = 'secondary' if status_id == unit.status else 'primary'
                ui.button(
                    f'{status_id} - {status_text}',
                    color=color_btn,
                    ).classes('w-full').props('align=left').on_click(lambda status_id=status_id: send_status(status_id))
    
    
    async def send_status(status_id: int):
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
        unit_overview.unit_overview.refresh()
        mission_units.refresh()
        status_tableau.refresh()
    
    unit = get_unit(unit_label)
    if not unit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    token = app.storage.user.get('token')
    user = await get_current_user(token)
    
    if user.username == unit_label:
        pass
    elif user.permission == Permission.admin:
        pass
    else:
        ui.navigate.to('/units')
        return
    
    await status_tableau(unit)
    