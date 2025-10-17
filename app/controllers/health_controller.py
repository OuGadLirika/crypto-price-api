from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Any

from aiohttp import web
from sqlalchemy import text


class HealthController:
    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    async def check(self, request: web.Request) -> web.Response:
        """
        Health check endpoint.
        
        Returns application health status including database connectivity.
        """
        health_data: Dict[str, Any] = {
            "status": "ok",
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        }
        
        try:
            async with self._session_factory() as session:
                result = await session.execute(text("SELECT 1"))
                result.scalar_one()
            health_data["database"] = "connected"
        except Exception as e:
            health_data["status"] = "degraded"
            health_data["database"] = f"error: {str(e)}"
            return web.json_response(health_data, status=503)
        
        return web.json_response(health_data)
