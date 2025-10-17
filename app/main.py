from __future__ import annotations

import asyncio
import logging
import os

from aiohttp import web
from aiohttp_apispec import setup_aiohttp_apispec, docs

from app.config import AppConfig
from app.controllers.health_controller import HealthController
from app.controllers.metrics_controller import MetricsController
from app.controllers.price_controller import PriceController
from app.db.engine import Base, create_engine_and_sessionmaker
from app.middleware.error_middleware import error_middleware
from app.middleware.metrics_middleware import metrics_middleware
from app.services.currency_service import CurrencyService
from app.services.exchange_service import ExchangeService
from app.services.metrics_service import MetricsService


logger = logging.getLogger(__name__)


async def _init_db(app: web.Application) -> None:
    config = app["config"]
    if config.env == "production" and not config.run_create_all:
        return
    engine = app["db_engine"]
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def _dispose_db(app: web.Application) -> None:
    await app["db_engine"].dispose()


async def _dispose_exchange(app: web.Application) -> None:
    await app["exchange_service"].close()


async def create_app(config: AppConfig | None = None) -> web.Application:
    if config is None:
        config = AppConfig.load()

    if config.enable_uvloop:
        try:
            import uvloop
            uvloop.install()
        except ImportError:
            logger.warning(
                "uvloop requested but not installed, using default event loop"
            )

    engine, session_factory = create_engine_and_sessionmaker(config.database_url)

    app = web.Application(middlewares=[error_middleware, metrics_middleware])
    app["config"] = config
    app["db_engine"] = engine
    app["session_factory"] = session_factory
    app["debug"] = os.getenv("DEBUG", "0") in {"1", "true", "yes"}
    
    app["exchange_service"] = ExchangeService()
    
    metrics_service = MetricsService()
    app["metrics_service"] = metrics_service

    app.on_startup.append(_init_db)
    app.on_cleanup.append(_dispose_db)
    app.on_cleanup.append(_dispose_exchange)

    @docs(
        tags=["price"],
        summary="Get current price",
        description="Fetch last bid price for {currency}/USDT from KuCoin and save to database",
        parameters=[{
            "in": "path",
            "name": "currency",
            "schema": {"type": "string"},
            "required": True,
            "description": "Currency symbol (BTC, ETH, SOL, etc.)",
        }],
        responses={
            200: {"description": "Price fetched and saved"},
            400: {"description": "Invalid currency or not found"},
        },
    )
    async def get_price(request: web.Request):
        async with request.app["session_factory"]() as session:
            controller = PriceController(
                request.app["exchange_service"],
                CurrencyService(session, config.page_size)
            )
            return await controller.get_price(request)

    @docs(
        tags=["price"],
        summary="Get price history",
        description="Get paginated price history (page size: 10)",
        parameters=[{
            "in": "query",
            "name": "page",
            "schema": {"type": "integer", "default": 1},
            "required": False,
            "description": "Page number",
        }],
        responses={
            200: {"description": "History retrieved"},
        },
    )
    async def get_history(request: web.Request):
        async with request.app["session_factory"]() as session:
            controller = PriceController(
                request.app["exchange_service"],
                CurrencyService(session, config.page_size)
            )
            return await controller.get_history(request)

    @docs(
        tags=["price"],
        summary="Delete all history",
        description="Delete all price records",
        responses={
            200: {"description": "All records deleted"},
        },
    )
    async def delete_history(request: web.Request):
        async with request.app["session_factory"]() as session:
            controller = PriceController(
                request.app["exchange_service"],
                CurrencyService(session, config.page_size)
            )
            return await controller.delete_history(request)

    health_controller = HealthController(session_factory)
    metrics_controller = MetricsController(metrics_service)
    
    @docs(
        tags=["monitoring"],
        summary="Health check",
        description="Check application health and database connectivity",
        responses={
            200: {"description": "Application is healthy"},
            503: {"description": "Application is degraded"},
        },
    )
    async def health(request: web.Request):
        return await health_controller.check(request)
    
    @docs(
        tags=["monitoring"],
        summary="Application metrics",
        description="Get application metrics (requests, errors, uptime)",
        responses={
            200: {"description": "Metrics retrieved"},
        },
    )
    async def metrics(request: web.Request):
        return await metrics_controller.get_metrics(request)

    app.router.add_get("/health", health)
    app.router.add_get("/metrics", metrics)
    app.router.add_get("/price/{currency}", get_price)
    app.router.add_get("/price/history", get_history)
    app.router.add_delete("/price/history", delete_history)

    setup_aiohttp_apispec(
        app=app,
        title="Qorpo Crypto Price API",
        version="1.0.0",
        url="/api/docs/swagger.json",
        swagger_path="/docs",
    )

    return app


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    config = AppConfig.load()
    app = asyncio.run(create_app(config))
    web.run_app(app, host=config.host, port=config.port)


if __name__ == "__main__":
    main()
