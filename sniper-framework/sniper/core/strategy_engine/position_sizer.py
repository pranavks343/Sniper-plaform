"""
Position Sizing Engine
Implements Kelly Criterion, fixed fractional, and volatility-adjusted sizing.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from sniper.schemas.common import Regime


@dataclass
class SizeResult:
    quantity: int
    capital_at_risk: float
    risk_pct: float
    method: str
    rationale: str


class PositionSizer:
    """
    Computes optimal position size using three methods:
    1. Kelly Criterion — maximises geometric growth
    2. Fixed Fractional  — risk a fixed % of capital per trade
    3. Volatility-Adjusted — scale down in high-volatility regimes

    The final quantity is the minimum of all three (most conservative).
    """

    def __init__(
        self,
        max_risk_pct: float = 0.01,       # max 1% of capital per trade
        kelly_fraction: float = 0.25,     # fractional Kelly (quarter-Kelly)
        max_position_pct: float = 0.10,   # max 10% of capital in one position
    ) -> None:
        self.max_risk_pct = max_risk_pct
        self.kelly_fraction = kelly_fraction
        self.max_position_pct = max_position_pct

    # ------------------------------------------------------------------
    def compute(
        self,
        capital: float,
        entry_price: float,
        stop_loss_price: float,
        win_rate: float,
        avg_win: float,
        avg_loss: float,
        regime: Regime,
        atr: float | None = None,
    ) -> SizeResult:
        """
        Args:
            capital:          Total available capital (INR)
            entry_price:      Planned entry price per share
            stop_loss_price:  Hard stop loss price per share
            win_rate:         Historical win rate of the strategy (0-1)
            avg_win:          Average winning trade P&L (absolute INR)
            avg_loss:         Average losing trade P&L (absolute INR, positive)
            regime:           Current HMM-detected regime
            atr:              14-bar ATR value (optional, for volatility sizing)
        """
        if entry_price <= 0 or stop_loss_price <= 0:
            return SizeResult(0, 0.0, 0.0, "none", "Invalid prices")

        risk_per_share = abs(entry_price - stop_loss_price)
        if risk_per_share < 0.01:
            return SizeResult(0, 0.0, 0.0, "none", "Stop too tight")

        # ── 1. Fixed fractional ──────────────────────────────────────
        capital_at_risk = capital * self.max_risk_pct
        qty_fixed = math.floor(capital_at_risk / risk_per_share)

        # ── 2. Kelly Criterion ───────────────────────────────────────
        if avg_loss > 0:
            b = avg_win / avg_loss          # reward-to-risk ratio
            kelly_pct = win_rate - (1 - win_rate) / b
            kelly_pct = max(0.0, kelly_pct) * self.kelly_fraction
        else:
            kelly_pct = self.max_risk_pct

        kelly_capital = capital * kelly_pct
        qty_kelly = math.floor(kelly_capital / risk_per_share)

        # ── 3. Volatility-adjusted ───────────────────────────────────
        regime_scale = {
            Regime.TRENDING:       1.0,
            Regime.MEAN_REVERTING: 0.75,
            Regime.VOLATILE:       0.40,
        }.get(regime, 0.5)

        if atr is not None and entry_price > 0:
            vol_pct = atr / entry_price
            vol_scale = max(0.2, 1.0 - vol_pct * 10)
        else:
            vol_scale = 1.0

        qty_vol = math.floor(qty_fixed * regime_scale * vol_scale)

        # ── 4. Cap by max_position_pct ───────────────────────────────
        max_shares_by_capital = math.floor(
            (capital * self.max_position_pct) / entry_price
        )

        # ── Take the minimum (most conservative) ────────────────────
        final_qty = min(qty_fixed, qty_kelly, qty_vol, max_shares_by_capital)
        final_qty = max(0, final_qty)

        actual_risk = final_qty * risk_per_share
        risk_pct = actual_risk / capital if capital > 0 else 0.0

        method = "min(fixed_fractional, kelly, volatility_adjusted)"
        rationale = (
            f"Fixed={qty_fixed} Kelly={qty_kelly} Vol={qty_vol} "
            f"CapCap={max_shares_by_capital} → {final_qty} shares | "
            f"Regime={regime.value} scale={regime_scale:.2f}"
        )

        return SizeResult(
            quantity=final_qty,
            capital_at_risk=actual_risk,
            risk_pct=risk_pct,
            method=method,
            rationale=rationale,
        )

    def atr(self, highs: list[float], lows: list[float], closes: list[float], period: int = 14) -> float:
        """Calculate Average True Range."""
        if len(highs) < period + 1:
            return 0.0
        trs: list[float] = []
        for i in range(1, len(highs)):
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i - 1]),
                abs(lows[i] - closes[i - 1]),
            )
            trs.append(tr)
        arr = np.array(trs[-period:])
        return float(arr.mean())
