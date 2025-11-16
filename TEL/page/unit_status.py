from nicegui import ui, app
from fastapi import HTTPException, status

from TEL.model import UNIT_STATUS, Permission, Mission, Unit
from TEL.database.unit import get_unit, update_unit_status
from TEL.database.mission import get_mission_by_id
from TEL.authentication import get_current_user
from TEL.page import unit_overview
from TEL.page.mission_detail import mission_units

async def unit_status(unit_label: str):
    
    @ui.refreshable
    async def status_tableau(unit: Unit, mission: Mission | None):
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
        status_tableau.refresh()
        unit_overview.unit_overview.refresh()
        await update_unit_status(unit.label, status_id)    
        mission_units.refresh()
    
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
    
    mission = get_mission_by_id(unit.mission_id)
    
    await status_tableau(unit, mission)