from __future__ import annotations

from aiohttp import web


@web.middleware
async def request_context_middleware(request: web.Request, handler):
    # Placeholder for future auth/request-id logging, etc.
    return await handler(request)
