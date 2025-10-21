from nicegui import ui, app

from TEL.authentication import get_current_user, authenticate_user, get_password_hash
from TEL.page.admin_user import validate_password
from TEL.database.user import _get_user_by_id, update_user_data

async def logout():
    app.storage.user.clear()
    ui.navigate.to('/login')

async def profile_page() -> None:
    token = app.storage.user.get('token')
    user = await get_current_user(token)
    
    def change_password_dialog():
        input_pwd0.set_value('')
        input_pwd1.set_value('')
        input_pwd2.set_value('')
        pwd_change_dialog.open()
        
    async def change_password():
        current_user = authenticate_user(user.username, input_pwd0.value)
        if not current_user:
            ui.notify('Aktuelles Passwort überprüfen', type='warning')
            return
        changed_user = _get_user_by_id(current_user.id)
        changed_user.hashed_password = get_password_hash(input_pwd1.value)
        changed_user = await update_user_data(changed_user)
        pwd_change_dialog.close()
        input_pwd0.set_value('')
        input_pwd1.set_value('')
        input_pwd2.set_value('')
        ui.notify('Passwort erfolgreich gespeichert', type='positive')
    
    with ui.dialog() as pwd_change_dialog:
        with ui.card(align_items='center'):
            ui.label('Passwort ändern').classes('text-xl')
            input_pwd0 = ui.input('Aktuelles Passwort', password=True, password_toggle_button=True).classes('w-full')
            input_pwd1 = ui.input('Passwort', password=True, password_toggle_button=True, validation=validate_password).classes('w-full')
            input_pwd2 = ui.input('Passwort Abgleich', password=True, validation={'Passwörter stimmen nicht überein.': lambda value: value == input_pwd1.value}).classes('w-full')
            input_button = ui.button('Speichern', on_click=change_password, icon='save').classes('w-full')
            ui.button('Abbrechen', on_click=pwd_change_dialog.close, icon='cancel').classes('w-full')
            
            input_pwd1.on_value_change(input_pwd2.validate)
            input_pwd2.on_value_change(input_pwd1.validate)
            input_button.disable()
            input_button.bind_enabled_from(input_pwd1, 'error', lambda error: input_pwd1.value and not error)
            input_button.bind_enabled_from(input_pwd2, 'error', lambda error: input_pwd2.value and not error)
    
    with ui.row().classes('w-full justify-center'):
        with ui.card():
            with ui.row().classes('w-full justify-center'):
                ui.icon('o_badge', size='xl')
            with ui.row(align_items='center').classes('w-full justify-center'):                
                ui.label(user.name).classes('text-xl')
            with ui.row(align_items='center'):
                ui.icon('o_person', size='md')
                ui.label(user.username)
            with ui.row(align_items='center'):
                ui.icon('o_mail', size='md')
                ui.label(user.email)
    
    with ui.row().classes('w-full justify-center'):
        with ui.column():
            ui.button('Passwort ändern', on_click=change_password_dialog, icon='o_change_circle')
        with ui.column():
            ui.button('Logout', on_click=logout, icon='logout')
            