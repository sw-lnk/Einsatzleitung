import os
from datetime import timedelta
from nicegui import ui, app

from TEL.authentication import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, hash_permission, Permission, ACCESS_TOKEN_UNIT_EXPIRE_DAYS

async def login_page() -> None:
    async def login() -> None:
        user =  authenticate_user(username.value, password.value)
        if user:
            ui.notify('Login successfull', type='positive')
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            if user.permission == Permission.unit:
                expires_delta=timedelta(minutes=ACCESS_TOKEN_UNIT_EXPIRE_DAYS)
            token = create_access_token(data={'sub': user.username}, expires_delta=expires_delta)
            data = {
                'token': token,
                'permission': hash_permission(user.permission)
            }
            app.storage.user.update(data)
            
            if user.permission == Permission.unit:
                ui.navigate.to(f'/unit/{user.username}')
                return
            
            ui.navigate.to('/')
        else:
            ui.notify('Benutzername und Passwort überprüfen.', type='warning')            
    
    with ui.card(align_items='center').classes('absolute-center'):
        ui.image(os.path.join('TEL', 'data', 'logo_TEL.png')).classes('w-32 m-0 p-0')
        ui.label('Technische Einsatzleitung').classes('text-center text-bold')
        username = ui.input('Benutzername').on('keydown.enter', login).classes('w-full')
        password = ui.input('Passwort', password=True, password_toggle_button=True).on('keydown.enter', login).classes('w-full')
        ui.button('Log in', on_click=login, icon='login').classes('w-full')
    return None