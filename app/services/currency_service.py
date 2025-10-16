from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import ceil
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.currency_repository import CurrencyRepository
from app.models.currency import Currency


@dataclass(frozen=True)
class Page:
    items: Sequence[dict]
    page: int
    page_size: int
    total: int
    total_pages: int


class CurrencyService:
    def __init__(self, session: AsyncSession, page_size: int) -> None:
        self._session = session
        self._repo = CurrencyRepository(session)
        self._page_size = page_size

    async def record_current_price(self, currency: str, price: float) -> dict:
        now = datetime.now(tz=timezone.utc).replace(tzinfo=None, microsecond=0)
        entity = await self._repo.add(currency=currency.lower(), date_=now, price=price)
        await self._session.commit()
        return entity.to_dict()

    async def get_history(self, page: int) -> Page:
        if page < 1:
            page = 1
        items, total = await self._repo.list_paginated(page=page, page_size=self._page_size)
        total_pages = ceil(total / self._page_size) if total else 1
        return Page(
            items=[i.to_dict() for i in items],
            page=page,
            page_size=self._page_size,
            total=total,
            total_pages=total_pages,
        )

    async def delete_all(self) -> int:
        deleted = await self._repo.delete_all()
        await self._session.commit()
        return deleted
