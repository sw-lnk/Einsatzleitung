from nicegui import ui, app

from TEL.model import Mission, Message, Category, Status, Priority
from TEL.authentication import get_current_user, verify_permission
from TEL.database.mission import get_mission_by_id, get_mission_by_label, update_mission_data
from TEL.database.message import create_message

from TEL.page.dashboard import dashboard_page
from TEL.page.mission_detail import messages, mission_messages, mission_details

def validate_input(value: str):
    if len(value) == 0:
        return 'Angabe erforderlich'
    return None

async def mission_edit_page(mission_id: int):
    
    def check_mission_input(mission: Mission) -> bool:
        if input_street.error or input_mission_label.error:
            ui.notify('Eingabe prüfen.', type='warning')
            return False
        
        if input_mission_label.value != mission.label:
            if get_mission_by_label(input_mission_label.value):
                ui.notify('Einsatznummer bereits vorhanden', type='warning')
                return False
        
        return True
    
    async def safe_mission() -> None:
        mission = get_mission_by_id(mission_id)
        if not check_mission_input(mission):
            return
        
        mission.label = input_mission_label.value
        mission.street = input_street.value
        mission.street_no = input_street_no.value
        mission.zip_code = input_zip_code.value
        mission.category = input_mission_category.value
        mission.status = input_mission_status.value
        mission.comment = input_comment.value
        
        new_message = Message(
            content=f'Einsatzdetails aktualisiert: {mission.__repr__()}',
            prio=Priority.low,
            user_id=user.id,
            mission_id=mission.id,
        )
        messages.insert(0, new_message)
        mission_messages.refresh()
        
        await update_mission_data(mission)
        await create_message(new_message)
        
        ui.notify('Speichern erfolgreich', type='positive')
        mission_details.refresh()
        mission_messages.refresh()
        dashboard_page.refresh()
        # ui.navigate.to(f'/mission/{mission.id}')

    user = await get_current_user(app.storage.user.get('token'))
    mission = get_mission_by_id(mission_id)
    
    with ui.row().classes('w-full justify-center'), ui.card():
        with ui.row().classes('w-full justify-center'):
            ui.label('Einsatzdetails bearbeiten').classes('text-xl')        
        
        status_selection = [Status.new, Status.in_progress, Status.closed]
        if verify_permission('admin', app.storage.user.get('permission')):
            status_selection.append(Status.archived)
        input_mission_status = ui.select(status_selection, label='Status', value=mission.status).classes('w-48').on('keydown.enter', safe_mission)
        
        with ui.row().classes('w-full justify-between'):
            input_mission_label = ui.input('Einsatznummer', value=mission.label, validation=validate_input).classes('w-48').on('keydown.enter', safe_mission)
            input_mission_category = ui.select([Category.fire, Category.th, Category.cbrn], label='Kategorie', value=mission.category).classes('w-48').on('keydown.enter', safe_mission)
        
        with ui.row().classes('w-full justify-between'):
            input_street = ui.input('Straße', value=mission.street, validation=validate_input).classes('w-48').on('keydown.enter', safe_mission)
            input_street_no = ui.input('Hausnummer', value=mission.street_no).classes('w-24').on('keydown.enter', safe_mission)
            input_zip_code = ui.input('PLZ', value=mission.zip_code).classes('w-24').on('keydown.enter', safe_mission)
        
        input_comment = ui.textarea('Bemerkung', value=mission.comment).classes('w-full')
            
        with ui.row().classes('w-full justify-center'):
            ui.button('Speichern', on_click=safe_mission, icon='save')
            ui.button('Einsatz', on_click=lambda: ui.navigate.to(f'/mission/{mission.id}'), icon='search')