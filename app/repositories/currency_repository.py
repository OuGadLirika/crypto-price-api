from __future__ import annotations

from decimal import Decimal
from typing import Sequence

from sqlalchemy import delete, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.currency import Currency


class CurrencyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, currency: str, date_, price: Decimal) -> Currency:
        entity = Currency(currency=currency, date_=date_, price=price)
        self._session.add(entity)
        await self._session.flush()
        return entity

    async def list_paginated(self, page: int, page_size: int) -> tuple[Sequence[Currency], int]:
        stmt = select(Currency).order_by(Currency.date_.desc(), Currency.id.desc()).offset((page - 1) * page_size).limit(page_size)
        count_stmt = select(func.count()).select_from(Currency)
        result = await self._session.execute(stmt)
        items = result.scalars().all()
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()
        return items, int(total)

    async def delete_all(self) -> int:
        stmt = delete(Currency)
        result = await self._session.execute(stmt)
        return result.rowcount or 0
