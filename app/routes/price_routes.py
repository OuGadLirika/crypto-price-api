from __future__ import annotations

from aiohttp import web

from app.controllers.price_controller import PriceController


def setup_price_routes(app: web.Application, controller: PriceController) -> None:
    router = app.router
    router.add_get("/price/{currency}", controller.get_price)
    router.add_get("/price/history", controller.get_history)
    router.add_delete("/price/history", controller.delete_history)
