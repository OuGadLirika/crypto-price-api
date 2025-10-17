"""
WSGI entrypoint for Gunicorn deployment.
"""
from __future__ import annotations
from aiohttp import web
from app.config import AppConfig
from app.main import create_app

async def app() -> web.Application:
    config = AppConfig.load()
    return await create_app(config)
