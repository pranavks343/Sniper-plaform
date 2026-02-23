"""
Real-time and historical market data via Yahoo Finance (yfinance).

Usage:
    from app.utils.market_data import MarketDataService
    svc = MarketDataService()
    price = svc.get_price("RELIANCE.NS")         # live price
    bars  = svc.get_historical("NIFTY50.NS", period="1mo", interval="1d")
"""
from __future__ import annotations

import asyncio
from datetime import datetime
from functools import lru_cache
from typing import Any

from app.utils.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Symbol helpers
# ---------------------------------------------------------------------------

# Common NSE symbol suffixes for Yahoo Finance
_NSE_SUFFIX = ".NS"
_BSE_SUFFIX = ".BO"

# Indices (no suffix needed for these)
_INDEX_SYMBOLS = {
    "NIFTY", "NIFTY50", "NIFTY 50",
    "SENSEX", "BSE",
    "BANKNIFTY", "NIFTYBANK",
}

# Map common shorthand → Yahoo Finance ticker
_SYMBOL_MAP: dict[str, str] = {
    "NIFTY": "^NSEI",
    "NIFTY50": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "NIFTYBANK": "^NSEBANK",
    "SENSEX": "^BSESN",
}


def _to_yahoo_ticker(symbol: str) -> str:
    """Convert a plain symbol to its Yahoo Finance ticker."""
    s = symbol.strip().upper()
    if s in _SYMBOL_MAP:
        return _SYMBOL_MAP[s]
    # Already has a suffix
    if "." in s:
        return s
    # Default to NSE
    return s + _NSE_SUFFIX


# ---------------------------------------------------------------------------
# MarketDataService
# ---------------------------------------------------------------------------

class MarketDataService:
    """Thin wrapper around yfinance for price data."""

    def __init__(self) -> None:
        try:
            import yfinance as yf  # noqa: F401
            self._available = True
        except ImportError:
            logger.warning("yfinance not installed — market data unavailable. Run: pip install yfinance")
            self._available = False

    # ------------------------------------------------------------------
    # Live price
    # ------------------------------------------------------------------

    def get_price(self, symbol: str) -> float | None:
        """Return the latest trade price for *symbol*. Returns None on failure."""
        if not self._available:
            return None
        import yfinance as yf
        ticker = _to_yahoo_ticker(symbol)
        try:
            info = yf.Ticker(ticker).fast_info
            price = getattr(info, "last_price", None) or getattr(info, "regular_market_price", None)
            if price is not None:
                logger.debug("Live price %s (ticker=%s): %.4f", symbol, ticker, price)
                return float(price)
        except Exception as exc:
            logger.warning("get_price failed for %s: %s", symbol, exc)
        return None

    async def aget_price(self, symbol: str) -> float | None:
        """Async wrapper — runs get_price in a thread pool."""
        return await asyncio.to_thread(self.get_price, symbol)

    def get_price_or_default(self, symbol: str, default: float = 100.0) -> float:
        """Return live price or *default* if unavailable."""
        price = self.get_price(symbol)
        if price is None:
            logger.debug("Using default price %.2f for %s", default, symbol)
            return default
        return price

    async def aget_price_or_default(self, symbol: str, default: float = 100.0) -> float:
        return await asyncio.to_thread(self.get_price_or_default, symbol, default)

    # ------------------------------------------------------------------
    # Historical OHLCV bars
    # ------------------------------------------------------------------

    def get_historical(
        self,
        symbol: str,
        period: str = "1mo",
        interval: str = "1d",
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """
        Return OHLCV bars as a list of dicts.

        period  : '1d','5d','1mo','3mo','6mo','1y','2y','5y','10y','ytd','max'
        interval: '1m','2m','5m','15m','30m','60m','90m','1h','1d','5d','1wk','1mo','3mo'
        """
        if not self._available:
            return []
        import yfinance as yf
        ticker = _to_yahoo_ticker(symbol)
        try:
            t = yf.Ticker(ticker)
            if start and end:
                df = t.history(start=start, end=end, interval=interval)
            else:
                df = t.history(period=period, interval=interval)

            if df.empty:
                logger.warning("No historical data for %s (ticker=%s)", symbol, ticker)
                return []

            bars = []
            for ts, row in df.iterrows():
                bars.append({
                    "timestamp": ts.isoformat() if hasattr(ts, "isoformat") else str(ts),
                    "open": float(row.get("Open", 0)),
                    "high": float(row.get("High", 0)),
                    "low": float(row.get("Low", 0)),
                    "close": float(row.get("Close", 0)),
                    "volume": int(row.get("Volume", 0)),
                })
            logger.info("Fetched %d bars for %s (%s / %s)", len(bars), symbol, period, interval)
            return bars
        except Exception as exc:
            logger.warning("get_historical failed for %s: %s", symbol, exc)
            return []

    async def aget_historical(
        self,
        symbol: str,
        period: str = "1mo",
        interval: str = "1d",
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Async wrapper for get_historical."""
        return await asyncio.to_thread(self.get_historical, symbol, period, interval, start, end)

    # ------------------------------------------------------------------
    # Batch prices
    # ------------------------------------------------------------------

    def get_prices(self, symbols: list[str]) -> dict[str, float]:
        """Fetch prices for multiple symbols in one call."""
        if not self._available or not symbols:
            return {}
        import yfinance as yf
        tickers = [_to_yahoo_ticker(s) for s in symbols]
        result: dict[str, float] = {}
        try:
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
            if "Close" in data.columns:
                close = data["Close"].iloc[-1]
                for orig_sym, ticker in zip(symbols, tickers):
                    if ticker in close.index and not __import__("math").isnan(close[ticker]):
                        result[orig_sym] = float(close[ticker])
        except Exception as exc:
            logger.warning("Batch get_prices failed: %s", exc)
        return result

    async def aget_prices(self, symbols: list[str]) -> dict[str, float]:
        return await asyncio.to_thread(self.get_prices, symbols)


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def get_market_data_service() -> MarketDataService:
    return MarketDataService()
