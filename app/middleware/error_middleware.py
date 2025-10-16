from __future__ import annotations

import json
import traceback
from aiohttp import web


@web.middleware
async def error_middleware(request: web.Request, handler):
    try:
        response = await handler(request)
        return response
    except web.HTTPException as http_exc:
        # Let aiohttp handle known HTTP errors
        raise http_exc
    except Exception as exc:  # noqa: BLE001
        # In production you might log the stack trace
        error_payload = {
            "status": "error",
            "message": str(exc),
        }
        # For debugging purposes, include stack only if debug enabled
        if request.app.get("debug"):
            error_payload["trace"] = traceback.format_exc()
        return web.json_response(error_payload, status=500)
