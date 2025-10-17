from __future__ import annotations

import logging
from datetime import datetime
from decimal import Decimal

import ccxt.async_support as ccxt


logger = logging.getLogger(__name__)


class ExchangeService:
    """Service to interact with exchanges via ccxt async API."""

    def __init__(self, exchange_id: str = "kucoin") -> None:
        if exchange_id != "kucoin":
            raise ValueError("Only 'kucoin' exchange is supported for this task")
        self._exchange = ccxt.kucoin({'enableRateLimit': True})
        logger.info(f"Initialized {exchange_id} exchange service")

    async def get_bid_price_usdt_pair(self, currency: str) -> Decimal:
        symbol = f"{currency.upper()}/USDT"
        logger.debug(f"Fetching bid price for {symbol}")
        try:
            ticker = await self._exchange.fetch_ticker(symbol)
        except ccxt.BadSymbol as e:
            logger.warning(f"Currency not found: {currency}")
            raise ValueError(f"Currency not found: {currency}") from e
        bid = ticker.get("bid")
        if bid is None:
            info = ticker.get("info") or {}
            bid = info.get("bestBid") or info.get("bid")
        if bid is None:
            logger.error(f"Bid price unavailable for {symbol}")
            raise RuntimeError("Bid price unavailable from exchange")
        logger.info(f"Fetched {symbol} bid price: {bid}")
        return Decimal(str(bid))

    async def close(self) -> None:
        logger.info("Closing exchange connection")
        await self._exchange.close()
