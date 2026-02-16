from __future__ import annotations

from collections import defaultdict
from datetime import datetime


class BarAggregator:
    def __init__(self) -> None:
        self._bars: dict[str, dict] = {}
        self._callbacks: list = []
        self._volumes = defaultdict(float)

    def add_tick(self, tick: dict) -> None:
        symbol = tick['symbol']
        price = float(tick['ltp'])
        volume = float(tick.get('volume', 0.0))

        bar = self._bars.setdefault(
            symbol,
            {'symbol': symbol, 'open': price, 'high': price, 'low': price, 'close': price, 'volume': 0.0, 'timestamp': datetime.utcnow()},
        )
        bar['high'] = max(bar['high'], price)
        bar['low'] = min(bar['low'], price)
        bar['close'] = price
        bar['volume'] += volume
        self._volumes[symbol] += volume

    def on_bar_complete(self, callback) -> None:
        self._callbacks.append(callback)

    def flush(self, symbol: str) -> dict | None:
        bar = self._bars.pop(symbol, None)
        if bar is None:
            return None
        for cb in self._callbacks:
            cb(bar)
        return bar

    def get_current_bar(self, symbol: str, timeframe: str = '1min') -> dict | None:
        _ = timeframe
        return self._bars.get(symbol)
