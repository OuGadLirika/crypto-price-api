from __future__ import annotations

from aiohttp import web

from app.services.metrics_service import MetricsService


class MetricsController:
    """Controller for exposing application metrics."""
    
    def __init__(self, metrics_service: MetricsService) -> None:
        self._metrics_service = metrics_service

    async def get_metrics(self, request: web.Request) -> web.Response:
        """
        Get application metrics.
        
        Returns metrics in JSON format suitable for monitoring systems.
        """
        metrics_data = self._metrics_service.get_metrics()
        return web.json_response(metrics_data)
