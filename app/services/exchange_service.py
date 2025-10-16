from __future__ import annotations

from datetime import datetime

import ccxt.async_support as ccxt  # type: ignore


class ExchangeService:
    """Service to interact with exchanges via ccxt async API."""

    def __init__(self, exchange_id: str = "kucoin") -> None:
        if exchange_id != "kucoin":
            raise ValueError("Only 'kucoin' exchange is supported for this task")
        self._exchange = ccxt.kucoin({'enableRateLimit': True})

    async def get_bid_price_usdt_pair(self, currency: str) -> float:
        symbol = f"{currency.upper()}/USDT"
        try:
            ticker = await self._exchange.fetch_ticker(symbol)
        except ccxt.BadSymbol as e:  # currency not found
            raise ValueError(f"Currency not found: {currency}") from e
        bid = ticker.get("bid")
        if bid is None:
            # Fallback: some exchanges return best bid via 'info'
            info = ticker.get("info") or {}
            bid = info.get("bestBid") or info.get("bid")
        if bid is None:
            raise RuntimeError("Bid price unavailable from exchange")
        return float(bid)

    async def close(self) -> None:
        await self._exchange.close()
