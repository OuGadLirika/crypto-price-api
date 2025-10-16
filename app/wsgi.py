from __future__ import annotations

# Gunicorn entrypoint using aiohttp worker class
# Run with: gunicorn -b 0.0.0.0:8000 app.wsgi:app --worker-class aiohttp.GunicornUVLoopWebWorker

import asyncio

from aiohttp import web

from app.config import AppConfig
from app.main import create_app


# Expose the app object for gunicorn
app: web.Application


def _make_app() -> web.Application:
    config = AppConfig.load()
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(create_app(config))


app = _make_app()
