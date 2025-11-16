from string import punctuation, digits, ascii_lowercase, ascii_uppercase
from nicegui import ui

from TEL.database import admin, user
from TEL.model import User, UserInfo, Permission
from TEL.authentication import get_password_hash

from TEL.page.card import card        

all_user = admin.get_all_user()
columns = [
    {'name': 'id', 'label': 'ID', 'field': 'id', 'sortable': True},
    {'name': 'name', 'label': 'Name', 'field': 'name', 'sortable': True, 'align': 'left'},
    {'name': 'username', 'label': 'Username', 'field': 'username', 'sortable': True, 'align': 'left'},
    {'name': 'email', 'label': 'eMail', 'field': 'email', 'align': 'left'},
    {'name': 'permission', 'label': 'Permission', 'field': 'permission', 'sortable': True, 'align': 'left'},
]

validate_password = {
    'Mindest Anzahl Zeichen: 8': lambda value: len(value)>=8,
    'Mindestens ein kleiner Buchstabe': lambda value: len(set(value).intersection(set(ascii_lowercase)))>0,
    'Mindestens ein großer Buchstabe': lambda value: len(set(value).intersection(set(ascii_uppercase)))>0,
    'Mindestens eine Zahl': lambda value: len(set(value).intersection(set(digits)))>0,
    'Mindestens ein Sonderzeichen': lambda value: len(set(value).intersection(set(punctuation)))>0,
}

validate_input = {'Eingabe überprüfen': lambda value: len(value)>=5}

def validate_email(email:str) -> bool:
    if '@' not in email:
        return 'Keine gültige Mailadresse'
    
    if '.' not in email:
        return 'Keine gültige Mailadresse'
    
    if email[-1] == '.':
        return 'Keine gültige Mailadresse'

    #test.mail@mail.com -> moc.liam@liam.test
    re_email = email[::-1]
    if re_email.index('.') > re_email.index('@'):
        return 'Keine gültige Mailadresse'
    
    return


@ui.refreshable
def admin_user_page() -> None:
    
    def clear_input():
        input_id.set_value('')
        input_name.set_value('')
        input_username.set_value('')
        input_email.set_value('')
        input_pwd1.set_value('')
        input_pwd2.set_value('')
        input_permission.set_value('')
        
    def new_user():
        clear_input()
        input_id.set_visibility(False)
        input_label.set_text('Neuer nutzer')
        input_button.set_text('Anlegen')
        input_button.on_click(create_new_user)
        
        user_dialog.open()        
    
    async def create_new_user():
        if not check_input_validation():
            return
        
        if user.get_user_by_username(input_username.value):
            ui.notify('Benutzername bereits vorhanden', type='warning')
            return
        
        try:
            new_user = await user.create_user(
                User(
                    username=input_username.value,
                    name=input_name.value,
                    email=input_email.value,
                    permission=input_permission.value,
                    hashed_password=get_password_hash(input_pwd1.value),
                )
            )
            
            if new_user:
                all_user.append(UserInfo.model_validate(new_user))
                admin_user_page.refresh()
            
            clear_input()
                
        except Exception:
            ui.notify('Eingaben überprüfen', type='warning')
    
    def set_user_values():
        user_id = user_table.selected[0]['id']
        user_db = user.get_user_by_id(int(user_id))
        
        input_id.set_value(user_id)
        input_name.set_value(user_db.name)
        input_username.set_value(user_db.username)
        input_email.set_value(user_db.email)
        input_permission.set_value(user_db.permission)
    
    def edit_user():
        clear_input()
        
        input_id.set_visibility(True)
        input_id.disable()
        
        input_label.set_text('Nutzer bearbeiten')
        input_button.set_text('Speichern')
        input_button.on_click(edit_selcted_user)
        
        set_user_values()
        user_dialog.open()
    
    
    async def edit_selcted_user():        
        new_pwd = True if len(input_pwd1.value) > 0  else False
        if not check_input_validation(new_pwd):
            return
        
        user_db = user._get_user_by_id(int(input_id.value))        
        user_db.name = input_name.value
        user_db.username = input_username.value
        user_db.email = input_email.value
        user_db.permission = input_permission.value
        if new_pwd:
            user_db.hashed_password = get_password_hash(input_pwd1.value)
        
        user_db = await user.update_user_data(user_db)
        
        for idx, u in enumerate(all_user):
            if u.id == user_db.id:
                all_user.pop(idx)
                all_user.append(user_db)
        
        ui.notify('Speichern erfolgreich', type='positive')
        
        clear_input()
        user_dialog.close()
        admin_user_page.refresh()
        
        
    def check_input_validation(check_password: bool = True):
        if input_name.error or (len(input_name.value) < 1):
            ui.notify('Namensangabe überprüfen.', type='warning')
            return False
        if input_username.error or (len(input_username.value) < 1):
            ui.notify('Angabe Benutzername überprüfen.', type='warning')
            return False
        if input_email.error or (len(input_email.value) < 1):
            ui.notify(input_email.error, type='warning')
            return False

        if check_password:
            
            if input_pwd1.error or (len(input_pwd1.value) < 1):
                ui.notify(input_pwd1.error, type='warning')
                return False
            if input_pwd2.error or (len(input_pwd2.value) < 1):
                ui.notify(input_pwd2.error, type='warning')
                return False
            
        return True
    
    with ui.dialog() as user_dialog:
        with ui.card(align_items='center'):
            input_label = ui.label('Neuer nutzer').classes('text-xl')
            input_id = ui.input('User ID').classes('w-full')
            input_name = ui.input('Full Name', validation=validate_input).classes('w-full')
            input_username = ui.input('Username', validation=validate_input).classes('w-full')
            input_email = ui.input('User eMail', validation=validate_email).classes('w-full')
            input_pwd1 = ui.input('Password', password=True, password_toggle_button=True, validation=validate_password).classes('w-full')
            input_pwd2 = ui.input('Password Validation', password=True, validation={'Passwörter stimmen nicht überein.': lambda value: value == input_pwd1.value}).classes('w-full')
            input_permission = ui.select([None, Permission.read, Permission.write, Permission.unit, Permission.admin], label='Permission').classes('w-full')
            input_button = ui.button('Anlegen', icon='save').classes('w-full')
            
            input_pwd1.on_value_change(input_pwd2.validate)
            
    
    with ui.row().classes('w-full justify-center'):
        with ui.row():
            with ui.column():
                card(str(len(all_user)), 'Anzahl Nutzer', icon='person')
            with ui.column():
                card(str(len([u for u in all_user if u.permission == Permission.admin])), 'Anzahl Admins', icon='person')
            with ui.column():
                card(str(len([u for u in all_user if u.permission == Permission.write])), 'Anzahl Schreibend', icon='person')
            with ui.column():
                card(str(len([u for u in all_user if u.permission == Permission.read])), 'Anzahl Lesend', icon='person')
            with ui.column():
                card(str(len([u for u in all_user if u.permission is None])), 'Anzahl Sonstige', icon='person')
        
        with ui.column():
            user_table = ui.table(
                rows=[u.model_dump() for u in all_user],
                columns=columns,
                selection='single'
            )
        
        with ui.column():
            ui.button('Neuer Nutzer', on_click=new_user, icon='add_box').classes('w-full')
            edit_user_button = ui.button('Nutzer bearbeiten', on_click=edit_user, icon='edit').classes('w-full')
            edit_user_button.bind_enabled_from(user_table, 'selected', lambda selected: len(selected)>0)
