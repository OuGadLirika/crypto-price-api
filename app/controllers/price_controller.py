from __future__ import annotations

from aiohttp import web

from app.services.exchange_service import ExchangeService
from app.services.currency_service import CurrencyService
from app.services.validation import CurrencyValidator


class PriceController:
    def __init__(self, exchange_service: ExchangeService, currency_service: CurrencyService) -> None:
        self._exchange = exchange_service
        self._currency = currency_service

    async def get_price(self, request: web.Request) -> web.Response:
        raw = request.match_info.get("currency", "")
        try:
            currency_norm = CurrencyValidator.normalize_and_validate(raw)
        except ValueError:
            raise web.HTTPBadRequest(text="invalid currency")
        try:
            bid = await self._exchange.get_bid_price_usdt_pair(currency_norm)
        except ValueError:
            raise web.HTTPBadRequest(text="currency not found")
        data = await self._currency.record_current_price(currency=currency_norm, price=bid)
        return web.json_response({"status": "ok", "data": data})

    async def get_history(self, request: web.Request) -> web.Response:
        page_str = request.rel_url.query.get("page", "1")
        try:
            page = int(page_str)
        except ValueError:
            page = 1
        page_data = await self._currency.get_history(page=page)
        return web.json_response({"status": "ok", "data": page_data.__dict__})

    async def delete_history(self, request: web.Request) -> web.Response:
        deleted = await self._currency.delete_all()
        return web.json_response({"status": "ok", "deleted": deleted})
