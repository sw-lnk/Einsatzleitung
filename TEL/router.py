from nicegui import ui
from fastapi import APIRouter

from TEL.page import login, index, theme, profile, dashboard, admin
from TEL.page import exception  # noqa: F401 # Ignore to use exeption pages
from TEL.authentication import require_auth
from TEL.model.user import Permission

router = APIRouter(tags=['Pages'])

# --- Landing Page ---
@ui.page('/', api_router=router)
async def index_page():
    with theme.frame(''):
        index.index_page()

@ui.page('/login', api_router=router)
async def login_page():
    with theme.frame('Login'):
        await login.login_page()

@ui.page('/admin')
@require_auth(Permission.admin)
async def admin_page():
    with theme.frame(''):
        admin.admin_page()

@ui.page('/profil')
@require_auth(None)
async def profile_page():
    with theme.frame('Nutzerprofil'):
        await profile.profile_page()

@ui.page('/dashboard')
@require_auth(Permission.read)
async def dashboard_page():
    with theme.frame('Dashboard'):
        dashboard.dashboard_page()
