import os
from contextlib import contextmanager

from nicegui import ui

from TEL.page.navigation import navigation


@contextmanager
def frame(navigation_title: str):
    """Custom page frame to share the same styling and behavior across all pages"""
    ui.colors(primary='#6E93D6', secondary='#53B689', accent='#111B1E', positive='#53B689')
    with ui.header():
        ui.link(os.getenv('APP_TITLE'), target='/').classes(replace='text-white font-bold')
        ui.space()
        ui.label(navigation_title)
        ui.space()
        with ui.row():
            navigation()
    yield