import asyncio
from aiohttp import web
import pytest

from app.controllers.price_controller import PriceController
from app.services.validation import CurrencyValidator


class DummyExchange:
    async def get_bid_price_usdt_pair(self, currency: str) -> float:
        if currency.upper() == "FAKE":
            raise ValueError("Currency not found")
        return 123.45

    async def close(self):
        pass


class DummyCurrencyService:
    async def record_current_price(self, currency: str, price: float) -> dict:
        return {"currency": currency, "price": price, "id": 1, "date_": "2025-10-16T00:00:00"}

    async def get_history(self, page: int):
        return type("Page", (), {"__dict__": {"items": [], "page": page, "page_size": 10, "total": 0, "total_pages": 1}})()

    async def delete_all(self) -> int:
        return 5


@pytest.mark.asyncio
async def test_get_price_ok(aiohttp_client):
    async def handler(request):
        controller = PriceController(DummyExchange(), DummyCurrencyService())
        return await controller.get_price(request)

    app = web.Application()
    app.router.add_get('/price/{currency}', handler)
    client = await aiohttp_client(app)
    resp = await client.get('/price/BTC')
    assert resp.status == 200
    data = await resp.json()
    assert data['status'] == 'ok'
    assert data['data']['currency'] == 'BTC'


@pytest.mark.asyncio
async def test_get_price_bad_symbol(aiohttp_client):
    async def handler(request):
        controller = PriceController(DummyExchange(), DummyCurrencyService())
        return await controller.get_price(request)

    app = web.Application()
    app.router.add_get('/price/{currency}', handler)
    client = await aiohttp_client(app)
    resp = await client.get('/price/bad-coin')
    assert resp.status == 400


@pytest.mark.asyncio
async def test_get_price_not_found(aiohttp_client):
    async def handler(request):
        controller = PriceController(DummyExchange(), DummyCurrencyService())
        return await controller.get_price(request)

    app = web.Application()
    app.router.add_get('/price/{currency}', handler)
    client = await aiohttp_client(app)
    resp = await client.get('/price/FAKE')
    assert resp.status == 400


@pytest.mark.asyncio
async def test_history_and_delete(aiohttp_client):
    controller = PriceController(DummyExchange(), DummyCurrencyService())

    async def get_h(request):
        return await controller.get_history(request)

    async def del_h(request):
        return await controller.delete_history(request)

    app = web.Application()
    app.router.add_get('/price/history', get_h)
    app.router.add_delete('/price/history', del_h)
    client = await aiohttp_client(app)

    resp = await client.get('/price/history?page=2')
    assert resp.status == 200
    data = await resp.json()
    assert data['data']['page'] == 2

    resp2 = await client.delete('/price/history')
    assert resp2.status == 200
    data2 = await resp2.json()
    assert data2['deleted'] == 5
