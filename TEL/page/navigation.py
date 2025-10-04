from nicegui import ui

def link(text: str, target: str) -> None:
    ui.link(text, target).classes(replace='text-white border hover:border-sky-900 rounded px-3')

def navigation() -> None:
    link('Admin', '/admin')
    link('Dashboard', '/dashboard')
    link('Profil', '/profil')    
    