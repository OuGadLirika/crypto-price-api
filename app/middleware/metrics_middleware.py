from __future__ import annotations

from aiohttp import web
from aiohttp.web import middleware


@middleware
async def metrics_middleware(request: web.Request, handler):
    """
    Middleware to track request metrics.
    
    Increments request counter and error counter based on response status.
    """
    metrics_service = request.app.get("metrics_service")
    
    if metrics_service:
        metrics_service.increment_request_count()
    
    try:
        response = await handler(request)
        
        if metrics_service and response.status >= 400:
            metrics_service.increment_error_count()
        
        return response
    except Exception as e:
        if metrics_service:
            metrics_service.increment_error_count()
        raise
