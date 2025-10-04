"""
Einsatzleitung Management System
"""

import os
from dotenv import load_dotenv
from nicegui import ui, app

# from TEL.logger import logger
from TEL.database import database
from TEL import router

load_dotenv()

# =============================================================================
# APPLICATION STARTUP
# =============================================================================

async def start_up() -> None:
    database.create_db_and_tables()
    # logger.info('Started application.')
    

app.on_startup(start_up)

app.include_router(router.router)

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title=os.getenv('APP_TITLE'),
        favicon=os.getenv('APP_ICON'),
        port=9112,
        show=True,
        reload=True,
        storage_secret=os.getenv('APP_SECRET'),
        language='de-DE'
    )
