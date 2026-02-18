"""
Bar Aggregator
Converts raw tick stream into OHLCV bars of any timeframe.
Supports: 1m, 3m, 5m, 15m, 30m, 1h, 4h, 1d
"""
from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable


@dataclass
class Bar:
    symbol:    str
    timeframe: str          # e.g. "1m", "5m", "1h"
    open:      float
    high:      float
    low:       float
    close:     float
    volume:    float
    vwap:      float
    ts_open:   float        # unix timestamp of bar open
    ts_close:  float        # unix timestamp of bar close
    closed:    bool = False


TIMEFRAME_SECONDS: dict[str, int] = {
    "1m":  60,
    "3m":  180,
    "5m":  300,
    "15m": 900,
    "30m": 1800,
    "1h":  3600,
    "4h":  14400,
    "1d":  86400,
}

BarCallback = Callable[[Bar], None]


class BarAggregator:
    """
    Aggregates tick stream into OHLCV bars.

    Usage:
        agg = BarAggregator(timeframes=["1m", "5m"])
        agg.on_bar_close(my_handler)
        agg.process_tick({"symbol": "NIFTY", "price": 24500.0, "volume": 100, "ts": time.time()})
    """

    def __init__(self, timeframes: list[str] | None = None) -> None:
        self._timeframes = timeframes or ["1m", "5m", "15m"]
        for tf in self._timeframes:
            if tf not in TIMEFRAME_SECONDS:
                raise ValueError(f"Unknown timeframe: {tf}. Valid: {list(TIMEFRAME_SECONDS)}")

        # Current open bar: {symbol: {timeframe: Bar}}
        self._open_bars: dict[str, dict[str, Bar]] = defaultdict(dict)
        # Running VWAP accumulators: {symbol: {tf: (sum_pv, sum_v)}}
        self._vwap_acc: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(lambda: [0.0, 0.0]))
        self._callbacks: list[BarCallback] = []

    def on_bar_close(self, callback: BarCallback) -> None:
        self._callbacks.append(callback)

    def process_tick(self, tick: dict) -> list[Bar]:
        """
        Process one tick and return any bars that just closed.

        Args:
            tick: {symbol, price, volume, ts (unix seconds)}
        Returns:
            List of closed Bar objects (usually empty, occasionally 1+)
        """
        symbol = tick["symbol"]
        price  = float(tick["price"])
        volume = float(tick.get("volume", 0))
        ts     = float(tick.get("ts", time.time()))

        closed_bars: list[Bar] = []

        for tf in self._timeframes:
            period = TIMEFRAME_SECONDS[tf]
            bar_open_ts  = (int(ts) // period) * period
            bar_close_ts = bar_open_ts + period

            existing = self._open_bars[symbol].get(tf)

            # Bar boundary crossed — close the old bar, open a new one
            if existing and existing.ts_open != bar_open_ts:
                existing.closed = True
                existing.vwap = (
                    self._vwap_acc[symbol][tf][0] / self._vwap_acc[symbol][tf][1]
                    if self._vwap_acc[symbol][tf][1] > 0 else existing.close
                )
                closed_bars.append(existing)
                for cb in self._callbacks:
                    try:
                        cb(existing)
                    except Exception:
                        pass
                # Reset VWAP accumulators
                self._vwap_acc[symbol][tf] = [0.0, 0.0]
                existing = None

            if existing is None:
                self._open_bars[symbol][tf] = Bar(
                    symbol=symbol, timeframe=tf,
                    open=price, high=price, low=price, close=price,
                    volume=volume, vwap=price,
                    ts_open=bar_open_ts, ts_close=bar_close_ts,
                )
            else:
                existing.high   = max(existing.high, price)
                existing.low    = min(existing.low, price)
                existing.close  = price
                existing.volume += volume

            # Update VWAP accumulators
            self._vwap_acc[symbol][tf][0] += price * volume
            self._vwap_acc[symbol][tf][1] += volume

        return closed_bars

    def get_open_bar(self, symbol: str, timeframe: str) -> Bar | None:
        return self._open_bars.get(symbol, {}).get(timeframe)

    def add_timeframe(self, tf: str) -> None:
        if tf not in TIMEFRAME_SECONDS:
            raise ValueError(f"Unknown timeframe: {tf}")
        if tf not in self._timeframes:
            self._timeframes.append(tf)
