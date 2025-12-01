import os
from nicegui import ui, app

from TEL.model import Mission, Message, Priority, Category, Status
from TEL.database.mission import get_mission_by_label, create_mission
from TEL.database.message import create_message
from TEL.authentication import get_current_user
from TEL.page.utils import validate_input, mission_messages
from TEL.page.dashboard import dashboard_page

PLZ = os.getenv('ZIP_CODE')

async def mission_new_page():
    def check_mission_input() -> bool:
        if not input_mission_category.value:
            ui.notify('Einsatzkategorie angeben.', type='warning')
            return False
        
        if input_street.error or input_mission_label.error:
            ui.notify('Eingabe prüfen.', type='warning')
            return False
        
        if input_mission_label.value:
            if get_mission_by_label(input_mission_label.value):
                ui.notify('Einsatznummer bereits vorhanden', type='warning')
                return False
        
        return True
        
    async def safe_mission() -> None:
        if not check_mission_input():
            return
        
        mission = Mission(
            label = input_mission_label.value,
            street = input_street.value,
            street_no = input_street_no.value,
            zip_code=input_zip_code.value,
            category = input_mission_category.value,
            status = Status.new,
            comment=input_comment.value,
        )  
        
        mission = await create_mission(mission)
        
        new_message = Message(
            content=f'Einsatzdetails aktualisiert: {mission.__repr__()}',
            prio=Priority.low,
            user_id=user.id,
            mission_id=mission.id,
        )        
        
        await create_message(new_message)
        mission_messages.refresh()
        dashboard_page.refresh()
        ui.notify('Speichern erfolgreich', type='positive')
        ui.navigate.to(f'/mission/{mission.id}')
    
    user = await get_current_user(app.storage.user.get('token'))
    
    with ui.row().classes('w-full justify-center'), ui.card(align_items='center'):
        with ui.row().classes('w-full justify-center'):
            ui.label('Einsatz anlegen').classes('text-xl')
        
        with ui.row().classes('w-full justify-between'):
            input_mission_label = ui.input('Einsatznummer', validation=validate_input).classes('w-48')
            input_mission_category = ui.select([Category.fire, Category.th, Category.cbrn], label='Kategorie').classes('w-48')
        
        with ui.row().classes('w-full justify-between'):
            input_street = ui.input('Straße', validation=validate_input).classes('w-48')
            input_street_no = ui.input('Hausnummer').classes('w-24')
            input_zip_code = ui.input('Postleitzahl', value=PLZ).classes('w-24')
        
        input_comment = ui.textarea(label='Bemerkung').classes('w-full')
        
        with ui.row().classes('w-full justify-center'):
            ui.button('Speichern', on_click=safe_mission, icon='save')
