from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from app.models.schemas.common import Direction, Regime


@dataclass
class TradingSignal:
    direction: Direction
    confidence: float
    entry_price: float
    expected_hold_time: int


class SignalGenerator:
    def calculate_ema(self, prices: np.ndarray, period: int) -> float:  
        if len(prices) < period:
            return float(prices[-1])
        alpha = 2 / (period + 1)
        ema = prices[0]
        for price in prices[1:]:
            ema = alpha * price + (1 - alpha) * ema
        return float(ema)

    def calculate_rsi(self, prices: np.ndarray, period: int = 14) -> float:
        delta = np.diff(prices)
        gains = np.where(delta > 0, delta, 0)
        losses = np.where(delta < 0, -delta, 0)
        avg_gain = np.mean(gains[-period:]) if len(gains) >= period else np.mean(gains)
        avg_loss = np.mean(losses[-period:]) if len(losses) >= period else np.mean(losses)
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return float(100 - (100 / (1 + rs)))

    def _macd(self, prices: np.ndarray) -> tuple[float, float]:
        ema12 = self.calculate_ema(prices, 12)
        ema26 = self.calculate_ema(prices, 26)
        macd = ema12 - ema26
        signal = macd * 0.8
        return macd, signal

    def generate_signals(self, bars: list[dict], regime: Regime) -> list[TradingSignal]:
        if regime != Regime.TRENDING or len(bars) < 60:
            return []

        prices = np.array([bar['close'] for bar in bars], dtype=float)
        volumes = np.array([bar.get('volume', 0.0) for bar in bars], dtype=float)

        ema_fast = self.calculate_ema(prices[-60:], 20)
        ema_slow = self.calculate_ema(prices[-60:], 50)
        rsi = self.calculate_rsi(prices[-60:], 14)
        macd, macd_signal = self._macd(prices[-60:])
        volume_ok = volumes[-1] > np.mean(volumes[-20:])

        votes = 0
        if ema_fast > ema_slow:
            votes += 1
        if rsi > 55:
            votes += 1
        if macd > macd_signal:
            votes += 1
        if volume_ok:
            votes += 1

        if votes < 3:
            return []

        confidence = min(0.95, 0.5 + votes * 0.1)
        return [
            TradingSignal(
                direction=Direction.BUY,
                confidence=confidence,
                entry_price=float(prices[-1]),
                expected_hold_time=45,
            )
        ]
