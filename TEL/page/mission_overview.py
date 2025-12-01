from nicegui import ui, app       

from TEL.page.card import card
from TEL.page.dashboard import dashboard_page
from TEL.database.mission import get_all_mission, get_mission_by_id, archiv_mission, reactivate_mission
from TEL.model import Status, Permission
from TEL.authentication import verify_permission

columns = [
    {'name': 'id', 'label': 'ID', 'field': 'id', 'sortable': True},
    {'name': 'label', 'label': 'Einsatz-Nr.', 'field': 'label', 'sortable': True, 'align': 'right'},
    {'name': 'street', 'label': 'Anschrift', 'field': 'street', 'align': 'left'},
    {'name': 'category', 'label': 'Art', 'field': 'category', 'align': 'right'},
    {'name': 'status', 'label': 'Status', 'field': 'status', 'sortable': True, 'align': 'right'},
]

@ui.refreshable
def mission_overview_page(archived: bool = True) -> None:
    all_missions = get_all_mission(archived)
    
    def hide_elements():
        permission = app.storage.user.get('permission')
        if (permission is None) or verify_permission(Permission.read, permission):
            new_mission_button.set_visibility(False)
        else:
            new_mission_button.set_visibility(True)
            
        archiv_mission_button.set_visibility(verify_permission(Permission.admin, permission))

       
    def show_mission_detail():
        mission_id = mission_table.selected[0]['id']
        ui.navigate.to(f'/mission/{mission_id}')
    
    
    def open_archiv_dialog():
        
        async def clicked_archiv_mission():        
            await archiv_mission(mission_id)
            archiv_dialog.close()
            mission_overview_page.refresh()
            dashboard_page.refresh()
            
        async def clicked_reactivate_mission():        
            await reactivate_mission(mission_id)
            archiv_dialog.close()
            mission_overview_page.refresh()
            dashboard_page.refresh()
        
        mission_id = mission_table.selected[0]['id']
        mission = get_mission_by_id(mission_id)
        with ui.dialog() as archiv_dialog, ui.card():
            with ui.row().classes('w-full justify-center'):
                if mission.status != Status.archived:
                    ui.label('Einsatz archivieren?').classes('text-xl')
                else:
                    ui.label('Einsatz reaktivieren?').classes('text-xl')
            with ui.row():
                if mission.status != Status.archived:
                    ui.button('Archivieren', on_click=clicked_archiv_mission, icon='archive').classes('bg-orange')
                else:
                    ui.button('Reaktivieren', on_click=clicked_reactivate_mission, icon='refresh').classes('bg-green')
                ui.button('Abbrechen', on_click=archiv_dialog.close, icon='cancel')
        archiv_dialog.open()       
                    
    with ui.row(align_items='stretch').classes('w-full justify-center'):
        
        with ui.row().classes('w-full justify-center'):
            with ui.row():
                with ui.column():
                    card(str(len([m for m in all_missions if m.status == Status.new])), 'Einsatz Neu', icon='o_control_point')
                with ui.column():
                    card(str(len([m for m in all_missions if m.status == Status.in_progress])), 'Einsatz In Arbeit', icon='o_change_circle')
                with ui.column():
                    card(str(len([m for m in all_missions if m.status == Status.closed])), 'Einsatz Abgeschlossen', icon='o_flag_circle')
                with ui.column():
                    card(str(len(all_missions)), 'Einsätze gesamt', icon='o_info')

        
        with ui.row().classes('w-full justify-center'):
            
            with ui.column():                
                mission_table = ui.table(
                    rows=[m.model_dump() for m in all_missions],
                    columns=columns,
                    selection='single'
                )
            
            with ui.column():
                new_mission_button = ui.button('Neuer Einsatz', icon='add_box', on_click=lambda: ui.navigate.to('mission/new')).classes('w-full')
                detail_mission_button = ui.button('Einsatz Details', on_click=show_mission_detail, icon='article').classes('w-full')
                detail_mission_button.bind_enabled_from(mission_table, 'selected', lambda selected: len(selected)>0)
                
                archiv_mission_button = ui.button('Einsatz Archiv', on_click=open_archiv_dialog, icon='archive').classes('w-full')
                archiv_mission_button.bind_enabled_from(mission_table, 'selected', lambda selected: len(selected)>0)
                
    hide_elements()
        