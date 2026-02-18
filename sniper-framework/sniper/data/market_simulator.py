"""
Market Simulator
Generates synthetic tick/bar data for paper trading and backtesting.
Uses Geometric Brownian Motion with regime-dependent volatility.
"""
from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass
from typing import Iterator


@dataclass
class Tick:
    symbol:  str
    price:   float
    bid:     float
    ask:     float
    volume:  int
    ts:      float


class MarketSimulator:
    """
    Synthetic market data generator.

    Parameters are per-regime:
    - TRENDING:       low vol, positive drift
    - MEAN_REVERTING: low vol, zero drift, mean-pull
    - VOLATILE:       high vol, random drift
    """

    REGIME_PARAMS = {
        "TRENDING":       {"mu": 0.0001,  "sigma": 0.0008, "spread_bps": 5},
        "MEAN_REVERTING": {"mu": 0.0,     "sigma": 0.0006, "spread_bps": 4},
        "VOLATILE":       {"mu": 0.0,     "sigma": 0.0025, "spread_bps": 12},
    }

    def __init__(
        self,
        symbol:     str   = "NIFTY",
        start_price: float = 24500.0,
        regime:     str   = "TRENDING",
        seed:       int   = 42,
    ) -> None:
        self.symbol = symbol
        self._price = start_price
        self._regime = regime
        random.seed(seed)
        self._rng_state = random.getstate()

    # ------------------------------------------------------------------

    def next_tick(self, ts: float | None = None) -> Tick:
        """Generate one synthetic tick."""
        params = self.REGIME_PARAMS.get(self._regime, self.REGIME_PARAMS["TRENDING"])
        mu    = params["mu"]
        sigma = params["sigma"]

        # GBM step
        z = random.gauss(0, 1)
        self._price *= math.exp((mu - 0.5 * sigma ** 2) + sigma * z)
        self._price = max(1.0, self._price)

        spread_bps = params["spread_bps"]
        half_spread = self._price * spread_bps / 10000 / 2
        volume = random.randint(50, 5000)

        return Tick(
            symbol=self.symbol,
            price=round(self._price, 2),
            bid=round(self._price - half_spread, 2),
            ask=round(self._price + half_spread, 2),
            volume=volume,
            ts=ts or time.time(),
        )

    def stream(self, n_ticks: int = 1000, interval_s: float = 0.0) -> Iterator[Tick]:
        """Yield n_ticks synthetic ticks."""
        ts = time.time()
        for _ in range(n_ticks):
            yield self.next_tick(ts)
            ts += interval_s or 1.0

    def set_regime(self, regime: str) -> None:
        if regime not in self.REGIME_PARAMS:
            raise ValueError(f"Unknown regime: {regime}. Valid: {list(self.REGIME_PARAMS)}")
        self._regime = regime

    @property
    def current_price(self) -> float:
        return round(self._price, 2)
