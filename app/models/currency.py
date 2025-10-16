from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.db.engine import Base


class Currency(Base):
    __tablename__ = "currencies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    currency: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    date_: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False, index=True)
    price: Mapped[float] = mapped_column(Numeric(precision=24, scale=10), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "currency": self.currency,
            "date_": self.date_.isoformat(timespec="seconds"),
            "price": float(self.price),
        }
