from datetime import timedelta
from nicegui import ui, app

from TEL.authentication import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

async def login_page() -> None:
    async def login() -> None:
        user =  authenticate_user(username.value, password.value)
        if user:
            ui.notify('Login successfull', type='positive')
            token = create_access_token(data={'sub': user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
            data = {
                'token': token
            }
            app.storage.user.update(data)
            ui.navigate.to('/')
        else:
            ui.notify('Benutzername und Passwort überprüfen.', type='warning')            
    
    with ui.card().classes('absolute-center'):
        username = ui.input('Benutzername').on('keydown.enter', login).classes('w-full')
        password = ui.input('Passwort', password=True, password_toggle_button=True).on('keydown.enter', login).classes('w-full')
        ui.button('Log in', on_click=login).classes('w-full')
    return None