from nicegui import ui, app

async def logout():
    app.storage.user.clear()
    ui.navigate.to('/login')

def link(text: str, target: str) -> None:
    ui.link(text, target).classes(replace='text-white border hover:border-sky-900 rounded px-3')

def navigation() -> None:
    # link('Admin - User', '/admin/user')
    # link('Admin - Einsatz', '/admin/mission')
    # link('Dashboard', '/dashboard')
    link('Einsätze', '/mission')
    link('Profil', '/profil')
    