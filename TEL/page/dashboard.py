import os
import datetime as dt
from nicegui import ui    

from TEL.model import Status
from TEL.database.unit import get_total_stuff
from TEL.database.mission import get_all_mission
from TEL.page.card import card 

def stuff_card(text: str, number: int, underline: bool = False):
    with ui.card(align_items='center').classes('w-36'):
        ui.label(text)
        ui.label(number).classes(f'text-xl {'underline' if underline else ''}')

@ui.refreshable
def dashboard_page() -> None:
    with ui.card(align_items='center').classes('w-full'):       
        
        ui.label('Einsatzübersicht').classes('text-xl bolt')  
        all_missions = get_all_mission()
        with ui.row().classes('w-full justify-center'):
            with ui.column():
                card(str(len([m for m in all_missions if m.status == Status.new])), 'Einsatz Neu', icon='o_control_point')
            with ui.column():
                card(str(len([m for m in all_missions if m.status == Status.in_progress])), 'Einsatz In Arbeit', icon='o_change_circle')
            with ui.column():
                card(str(len([m for m in all_missions if m.status == Status.closed])), 'Einsatz Abgeschlossen', icon='o_flag_circle')
            with ui.column():
                card(str(len(all_missions)), 'Einsätze gesamt', icon='o_info')
        
        ui.separator()
        
        ui.label('Kräfteübersicht').classes('text-xl bolt')        
        total_stuff = get_total_stuff()
        with ui.row(align_items='center').classes('w-full justify-center'):
            stuff_card('Verbandsführer', total_stuff['vf'])
            stuff_card('Zugführer', total_stuff['zf'])
            stuff_card('Gruppenführer', total_stuff['gf'])
            stuff_card('Mannschaft', total_stuff['ms'])
            stuff_card('Gesamt', total_stuff['total'], True)
            
        ui.separator()
        
        time = dt.datetime.now()
        time_str = time.strftime('%d.%m.%Y - %H:%M')
        time_str_t = time.strftime('%d%H%M%b%y')
        ui.label(time_str).classes('text-xl bolt')
        ui.label(time_str_t)

if int(os.getenv('RELOAD_DASHBOARD_AUTOMATICALLY', 0)):
    ui.timer(20, dashboard_page.refresh)
