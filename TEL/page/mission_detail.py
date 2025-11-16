from nicegui import ui, app
from fastapi import status
from fastapi.exceptions import HTTPException

from TEL.model import Mission, Message, Category, Status, Priority
from TEL.database.message import get_all_messages, create_message
from TEL.database.mission import get_mission_by_id, get_mission_by_label, update_mission_data
from TEL.authentication import get_current_user, verify_permission
from TEL.page.dashboard import dashboard_page

messages: list[Message] = get_all_messages()

@ui.refreshable
def mission_details(mission_id: int):
    mission = get_mission_by_id(mission_id)
    with ui.card():
        with ui.row(align_items='center'):
            ui.icon('o_location_on', size='xl')
            if mission.street_no:
                ui.label(' '.join([mission.street, mission.street_no])).classes('text-xl')
            else:
                ui.label(mission.street).classes('text-xl')
        with ui.row(align_items='center').classes('w-full justify-end'):
            ui.label(f'PLZ: {mission.zip_code}')
        with ui.row(align_items='center'):
            if mission.category == Category.fire:
                ui.icon('o_fire_extinguisher', size='md')
            elif mission.category == Category.th:
                ui.icon('o_build', size='md')
            elif mission.category == Category.cbrn:
                ui.icon('o_flare', size='md')
            ui.label(mission.category)
        with ui.row(align_items='center'):
            ui.icon('o_tag', size='md')
            ui.label(mission.label)
        with ui.row(align_items='center'):
            ui.icon('o_label', size='md')
            ui.label(mission.status)
            
            
def message_element(message: Message) -> None:
    if message.prio == Priority.top:
        msg_prio = 'no-shadow border-2 border-red-400'
        icon = 'flash_on'
        icon_size = 'sm'
    elif message.prio == Priority.high:
        msg_prio = 'no-shadow border-2 border-blue-400'
        icon = 'priority_high'
        icon_size = 'sm'
    elif message.prio == Priority.low:
        msg_prio = 'no-shadow border-2'
        icon = None
        icon_size = None
    else:
        msg_prio = None
        icon = 'o_info'
        icon_size = None
        
    with ui.card().classes('w-full').classes(msg_prio):
        text_style = 'text-xs text-gray-400 p-0 m-0'
        with ui.row(align_items='start').classes('w-full justify-between'):
            ui.label(message.content).classes('w-10/12')                                
            with ui.column(align_items='end').classes('w-auto'):
                ui.label(f'Priorität: {message.prio.value.capitalize()}').classes(text_style)
                if icon:
                    ui.icon(icon, size=icon_size)                
        with ui.row().classes('w-full justify-between'):
            ui.label(message.user_name if message.user_id else '').classes(text_style)
            ui.label(message.created_at.strftime("%d.%m.%Y - %H:%M:%S")).classes(text_style)


@ui.refreshable
def mission_messages(mission_id: int) -> None:
    if messages:
        for message in messages:
            if message.mission_id == mission_id:
                message_element(message)
    else:
        ui.label('No messages yet').classes('mx-auto my-36')

def validate_input(value: str):
    if len(value) == 0:
        return 'Angabe erforderlich'
    return None

async def mission_detail_page(mission_id: int):
    current_mission = get_mission_by_id(mission_id)
    if current_mission is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            'Mission ID is not known'
        )
    elif current_mission.status == Status.archived:
        with ui.row().classes('w-full justify-center'):
            with ui.card():
                with ui.row().classes('w-full justify-center'):
                    ui.icon('o_archive', size='xl')
                with ui.row().classes('w-full justify-center'):                
                    ui.label(current_mission.street).classes('text-xl')
                with ui.row(align_items='center').classes('w-full justify-center'):
                    ui.icon('o_tag', size='md')
                    ui.label(current_mission.label)
                with ui.row().classes('w-full justify-center'):
                    ui.label('Einsatz ist archiviert.')       
        
        return
        
    async def send() -> None:
        new_message = Message(
                mission_id=mission_id,
                content=text.value,
                user_name=user.name,
                user_id=user.id,
                prio=prio.value
            )
        messages.insert(0, new_message)
        text.set_value('')
        prio.set_value(Priority.medium)
        mission_messages.refresh()
        await create_message(new_message)

    def open_change_dialog():
        mission = get_mission_by_id(mission_id)
        input_street.set_value(mission.street) 
        input_street_no.set_value(mission.street_no)
        input_mission_label.set_value(mission.label)
        input_mission_category.set_value(mission.category)
        input_mission_status.set_value(mission.status)
        mission_change_dialog.open()
    
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
        mission.category = input_mission_category.value
        mission.status = input_mission_status.value    
        
        new_message = Message(
            content=f'Einsatzdetails aktualisiert: {mission.__repr__()}',
            prio=Priority.low,
            user_name=user.name,
            user_id=user.id,
            mission_id=mission.id,
        )
        messages.insert(0, new_message)
        mission_messages.refresh()
        
        await update_mission_data(mission)
        await create_message(new_message)
        
        ui.notify('Speichern erfolgreich', type='positive')
        mission_change_dialog.close()
        mission_details.refresh()
        mission_messages.refresh()
        dashboard_page.refresh()
    
    user = await get_current_user(app.storage.user.get('token'))
    
    with ui.dialog() as mission_change_dialog, ui.card(align_items='center'):
        with ui.row().classes('w-full justify-center'):
            ui.label('Einsatzdetails bearbeiten').classes('w-full text-xl')
        input_mission_label = ui.input('Einsatznummer', validation=validate_input).classes('w-full')
        input_street = ui.input('Straße', validation=validate_input).classes('w-full')
        input_street_no = ui.input('Hausnummer').classes('w-full')
        input_mission_category = ui.select([Category.fire, Category.th, Category.cbrn], label='Kategorie').classes('w-full')
        
        status_selection = [Status.new, Status.in_progress, Status.closed]
        if verify_permission('admin', app.storage.user.get('permission')):
            status_selection.append(Status.archived)
        input_mission_status = ui.select(status_selection, label='Status').classes('w-full')
        with ui.row().classes('w-full justify-center'):
            ui.button('Speichern', on_click=safe_mission, icon='save')
    
    with ui.row().classes('w-full justify-center'):
        with ui.column(align_items='center'):
            mission_details(mission_id)
            ui.button('Einsatz bearbeiten', on_click=open_change_dialog, icon='edit')
        
        with ui.column().classes('w-full max-w-2xl mx-auto items-stretch'):
            mission_messages(mission_id)
        
    with ui.footer().classes('border-t-2 bg-white'), ui.row(align_items='center').classes('w-full justify-center mx-5'):
            prio = ui.select(
                [Priority.low, Priority.medium, Priority.high, Priority.top],
                label='Priorität',
                value=Priority.medium).classes('w-1/12')
            
            text = ui.input(
                placeholder='Meldung',
                validation={'Min. Anzahl Zeichen 3': lambda value: len(value)>2}
                ).on('keydown.enter', send) \
                .classes('flex-grow border-2 rounded-lg p-2 bg-white')
            
            ui.button(
                'Senden',
                on_click=send,
                icon='send'
            ).bind_enabled_from(text, 'error', lambda error: text.value and not error)
