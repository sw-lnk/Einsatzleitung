from nicegui import ui, app
from fastapi import status
from fastapi.exceptions import HTTPException

from TEL.model import Message, Status, Priority
from TEL.database.message import create_message
from TEL.database.mission import get_mission_by_id
from TEL.authentication import get_current_user
from TEL.page.utils import mission_details, mission_messages, mission_units, mission_status_table

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
                user_id=user.id,
                prio=prio.value
            )
        text.set_value('')
        prio.set_value(Priority.medium)
        await create_message(new_message)
        mission_messages.refresh()
    
    user = await get_current_user(app.storage.user.get('token'))
    
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
            
    with ui.row().classes('w-full justify-center'):
        with ui.column(align_items='center'):
            mission_details(mission_id)
            mission_units(mission_id, text)
            mission_status_table(mission_id)
        
        with ui.column().classes('w-full max-w-2xl mx-auto items-stretch'):
            mission_messages(mission_id)
