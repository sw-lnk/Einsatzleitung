from nicegui import ui
from fastapi import APIRouter

from TEL.page import admin_user, login, index, theme, profile
from TEL.page import dashboard, mission_overview, mission_new, mission_detail
from TEL.page import unit_overview, unit_status
from TEL.page import exception  # noqa: F401 # Ignore to use exeption pages
from TEL.authentication import require_auth
from TEL.model import Permission

router = APIRouter(tags=['Pages'])

# --- Landing Page ---
@ui.page('/', api_router=router)
@require_auth(Permission.read)
async def index_page():
    with theme.frame(''):
        index.index_page()
        
@ui.page('/dashboard')
@require_auth(Permission.read)
async def dashboard_page():
    with theme.frame('Dashboard'):
        dashboard.dashboard_page()

@ui.page('/login', api_router=router)
async def login_page():
    await login.login_page()

@ui.page('/admin/user')
@require_auth(Permission.admin)
async def admin_page():
    with theme.frame(''):
        admin_user.admin_user_page()

@ui.page('/profil')
@require_auth(None)
async def profile_page():
    with theme.frame('Nutzerprofil'):
        await profile.profile_page()

@ui.page('/mission')
@require_auth(Permission.read)
async def mission_overview_page():
    with theme.frame('Einsatzübersicht'):
        mission_overview.mission_overview_page()

@ui.page('/mission/new')
@require_auth(Permission.write)
async def mission_new_page():
    with theme.frame(''):
        await mission_new.mission_new_page()

@ui.page('/mission/{mission_id}')
@require_auth(Permission.read)
async def mission_detail_page(mission_id: int):
    with theme.frame('Einsatzdetails'):
        await mission_detail.mission_detail_page(int(mission_id))

@ui.page('/admin/mission')
@require_auth(Permission.admin)
async def mission_admin_page():
    with theme.frame('Einsatzübersicht'):
        mission_overview.mission_overview_page(False)

@ui.page('/units')
@require_auth(Permission.read)
async def unit_page():
    with theme.frame('Einsatzübersicht'):
        await unit_overview.unit_page()

@ui.page('/unit/{unit_label}')
@require_auth(Permission.unit)
async def unit_status_page(unit_label: str):
    await unit_status.unit_status(unit_label)
