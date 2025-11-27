from nicegui import ui, app
from fastapi import HTTPException, status

from TEL.model import Permission
from TEL.database.unit import get_unit
from TEL.authentication import get_current_user
from TEL.page.unit_status_utils import status_tableau


async def unit_status(unit_label: str):
    
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
    
    await status_tableau(unit.label)
    