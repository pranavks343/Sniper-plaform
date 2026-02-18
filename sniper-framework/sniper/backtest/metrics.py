"""
Performance Metrics
Computes standard quantitative finance metrics from an equity curve.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence


@dataclass
class PerformanceMetrics:
    total_return_pct:  float
    cagr_pct:          float
    sharpe_ratio:      float
    sortino_ratio:     float
    calmar_ratio:      float
    max_drawdown_pct:  float
    win_rate_pct:      float
    profit_factor:     float
    avg_win:           float
    avg_loss:          float
    total_trades:      int
    winning_trades:    int
    losing_trades:     int
    expectancy:        float    # avg profit per trade
    annualised_vol_pct: float


class PerformanceCalculator:

    TRADING_DAYS = 252
    RISK_FREE_RATE = 0.065       # India 10Y bond ~6.5%

    def compute(
        self,
        equity_curve: list[float],   # daily equity values
        trades: list[dict],          # [{pnl, entry, exit, ...}]
        periods_per_year: int = 252,
    ) -> PerformanceMetrics:
        """
        Args:
            equity_curve: list of portfolio equity values (one per period)
            trades: list of closed trade dicts with at minimum {"pnl": float}
            periods_per_year: 252 for daily, 52 for weekly, etc.
        """
        n = len(equity_curve)
        if n < 2:
            return self._empty()

        returns = [
            (equity_curve[i] - equity_curve[i - 1]) / equity_curve[i - 1]
            for i in range(1, n)
        ]

        total_return = (equity_curve[-1] - equity_curve[0]) / equity_curve[0]
        years = n / periods_per_year
        cagr = (equity_curve[-1] / equity_curve[0]) ** (1 / max(years, 0.01)) - 1

        # Volatility
        mean_r = sum(returns) / len(returns)
        variance = sum((r - mean_r) ** 2 for r in returns) / max(len(returns) - 1, 1)
        vol = math.sqrt(variance * periods_per_year)

        # Sharpe
        rfr_per_period = self.RISK_FREE_RATE / periods_per_year
        excess = [r - rfr_per_period for r in returns]
        mean_excess = sum(excess) / len(excess)
        vol_excess = math.sqrt(sum((e - mean_excess) ** 2 for e in excess) / max(len(excess) - 1, 1))
        sharpe = (mean_excess * periods_per_year) / (vol_excess * math.sqrt(periods_per_year) + 1e-10)

        # Sortino (only downside deviation)
        downside = [min(r - rfr_per_period, 0) for r in returns]
        down_var = sum(d ** 2 for d in downside) / max(len(downside), 1)
        sortino = (mean_excess * periods_per_year) / (math.sqrt(down_var * periods_per_year) + 1e-10)

        # Max drawdown
        peak = equity_curve[0]
        max_dd = 0.0
        for e in equity_curve:
            peak = max(peak, e)
            dd = (peak - e) / peak
            max_dd = max(max_dd, dd)

        # Calmar
        calmar = cagr / (max_dd + 1e-10)

        # Trade statistics
        pnls = [t.get("pnl", 0.0) for t in trades]
        wins  = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p < 0]

        win_rate = len(wins) / max(len(pnls), 1)
        avg_win  = sum(wins)  / max(len(wins), 1)
        avg_loss = abs(sum(losses) / max(len(losses), 1))
        profit_factor = sum(wins) / (abs(sum(losses)) + 1e-10)
        expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)

        return PerformanceMetrics(
            total_return_pct=round(total_return * 100, 2),
            cagr_pct=round(cagr * 100, 2),
            sharpe_ratio=round(sharpe, 3),
            sortino_ratio=round(sortino, 3),
            calmar_ratio=round(calmar, 3),
            max_drawdown_pct=round(max_dd * 100, 2),
            win_rate_pct=round(win_rate * 100, 2),
            profit_factor=round(profit_factor, 3),
            avg_win=round(avg_win, 2),
            avg_loss=round(avg_loss, 2),
            total_trades=len(pnls),
            winning_trades=len(wins),
            losing_trades=len(losses),
            expectancy=round(expectancy, 2),
            annualised_vol_pct=round(vol * 100, 2),
        )

    @staticmethod
    def _empty() -> PerformanceMetrics:
        return PerformanceMetrics(
            total_return_pct=0, cagr_pct=0, sharpe_ratio=0, sortino_ratio=0,
            calmar_ratio=0, max_drawdown_pct=0, win_rate_pct=0, profit_factor=0,
            avg_win=0, avg_loss=0, total_trades=0, winning_trades=0,
            losing_trades=0, expectancy=0, annualised_vol_pct=0,
        )
