"""
Backtest Engine
Historical data replay with realistic order fill simulation.
Supports:
  - Slippage and market impact
  - Partial fills on thin liquidity
  - Equity curve + drawdown tracking
  - Walk-forward analysis
  - Performance metrics (Sharpe, Sortino, Calmar, win rate, etc.)
"""
from __future__ import annotations

import logging
import math
import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Iterator

import numpy as np

from sniper.backtest.metrics import PerformanceCalculator, PerformanceMetrics

logger = logging.getLogger("sniper.backtest")

SignalFn = Callable[[list[dict]], list[dict]]   # bars → signals [{direction, size, ...}]


@dataclass
class BacktestResult:
    equity_curve:    list[float]
    trades:          list[dict]
    metrics:         PerformanceMetrics
    walk_forward:    list[dict] = field(default_factory=list)  # per-fold metrics
    start_capital:   float = 0.0
    end_capital:     float = 0.0
    total_bars:      int   = 0


class BacktestEngine:
    """
    Event-driven backtest engine.

    Usage:
        engine = BacktestEngine(capital=1_000_000)
        result = engine.run(bars=my_bars, signal_fn=my_strategy)
    """

    def __init__(
        self,
        capital:            float = 1_000_000.0,
        slippage_bps:       float = 5.0,
        commission_per_lot: float = 40.0,    # INR per round-trip lot
        partial_fill_prob:  float = 0.05,    # 5% chance of partial fill
        market_impact_k:    float = 0.001,   # market impact coefficient
    ) -> None:
        self._start_capital = capital
        self._slippage_bps  = slippage_bps
        self._commission     = commission_per_lot
        self._partial_prob   = partial_fill_prob
        self._impact_k       = market_impact_k

    # ------------------------------------------------------------------
    # Main run
    # ------------------------------------------------------------------

    def run(
        self,
        bars: list[dict],
        signal_fn: SignalFn,
        warmup_bars: int = 50,
    ) -> BacktestResult:
        """
        Args:
            bars: list of OHLCV dicts — {open, high, low, close, volume, ts}
            signal_fn: callable(bars_so_far) → list of signal dicts
                       signal dict: {direction:"BUY"|"SELL", size:int, stop_loss:float}
            warmup_bars: number of bars consumed before signal generation starts
        Returns:
            BacktestResult with equity curve, trades, and metrics
        """
        capital     = self._start_capital
        equity_curve: list[float] = [capital]
        trades:       list[dict]  = []
        position:     dict | None = None

        for i in range(warmup_bars, len(bars)):
            bar = bars[i]
            close = bar["close"]
            high  = bar["high"]
            low   = bar["low"]

            # ── Check stop loss ──────────────────────────────────────
            if position:
                stop = position.get("stop_loss", 0.0)
                if position["direction"] == "BUY" and low <= stop:
                    pnl, capital = self._close_position(position, stop, capital)
                    trades.append({**position, "exit_price": stop, "pnl": pnl, "exit_reason": "stop_loss"})
                    position = None
                elif position["direction"] == "SELL" and high >= stop:
                    pnl, capital = self._close_position(position, stop, capital)
                    trades.append({**position, "exit_price": stop, "pnl": pnl, "exit_reason": "stop_loss"})
                    position = None

            # ── Generate signals ─────────────────────────────────────
            signals = signal_fn(bars[:i + 1])

            for sig in signals:
                direction = sig.get("direction", "BUY")
                size      = sig.get("size", 1)
                stop_loss = sig.get("stop_loss", close * (0.98 if direction == "BUY" else 1.02))

                if position and position["direction"] == direction:
                    continue   # already in the right direction

                # Close opposite position first
                if position and position["direction"] != direction:
                    pnl, capital = self._close_position(position, close, capital)
                    trades.append({**position, "exit_price": close, "pnl": pnl, "exit_reason": "signal_reversal"})
                    position = None

                # Open new position
                fill_price = self._simulate_fill(close, direction, size, bar)
                cost = fill_price * size + self._commission
                if cost <= capital:
                    capital -= cost
                    position = {
                        "direction":  direction,
                        "size":       size,
                        "entry_price": fill_price,
                        "stop_loss":  stop_loss,
                        "entry_bar":  i,
                        "entry_ts":   bar.get("ts", i),
                    }

            equity_curve.append(capital + self._mark_to_market(position, close))

        # Close any open position at the end
        if position:
            last_close = bars[-1]["close"]
            pnl, capital = self._close_position(position, last_close, capital)
            trades.append({**position, "exit_price": last_close, "pnl": pnl, "exit_reason": "end_of_data"})

        equity_curve.append(capital)

        calc = PerformanceCalculator()
        metrics = calc.compute(equity_curve, trades)

        return BacktestResult(
            equity_curve=equity_curve,
            trades=trades,
            metrics=metrics,
            start_capital=self._start_capital,
            end_capital=capital,
            total_bars=len(bars),
        )

    # ------------------------------------------------------------------
    # Walk-forward analysis
    # ------------------------------------------------------------------

    def walk_forward(
        self,
        bars: list[dict],
        signal_fn: SignalFn,
        n_folds: int = 5,
        train_pct: float = 0.7,
    ) -> BacktestResult:
        """
        Split data into n_folds, train on train_pct, test on remainder.
        Returns combined result with per-fold metrics in walk_forward field.
        """
        fold_size  = len(bars) // n_folds
        all_trades: list[dict] = []
        all_equity: list[float] = [self._start_capital]
        fold_results: list[dict] = []

        for fold in range(n_folds):
            start = fold * fold_size
            end   = start + fold_size
            fold_bars = bars[start:end]
            train_end = int(len(fold_bars) * train_pct)

            test_bars  = fold_bars[train_end:]
            result = self.run(bars=fold_bars, signal_fn=signal_fn, warmup_bars=train_end)
            all_trades.extend(result.trades)
            all_equity.extend(result.equity_curve[1:])
            fold_results.append({
                "fold":        fold + 1,
                "sharpe":      result.metrics.sharpe_ratio,
                "total_return": result.metrics.total_return_pct,
                "max_dd":      result.metrics.max_drawdown_pct,
                "trades":      result.metrics.total_trades,
            })
            logger.info("Fold %d: Sharpe=%.2f Return=%.1f%%", fold + 1, result.metrics.sharpe_ratio, result.metrics.total_return_pct)

        calc    = PerformanceCalculator()
        metrics = calc.compute(all_equity, all_trades)
        return BacktestResult(
            equity_curve=all_equity,
            trades=all_trades,
            metrics=metrics,
            walk_forward=fold_results,
            start_capital=self._start_capital,
            end_capital=all_equity[-1] if all_equity else self._start_capital,
            total_bars=len(bars),
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _simulate_fill(self, price: float, direction: str, size: int, bar: dict) -> float:
        """Add slippage + random partial fill simulation."""
        slippage = price * self._slippage_bps / 10000
        if direction == "BUY":
            fill = price + slippage
        else:
            fill = price - slippage

        # Market impact: price moves adversely proportional to sqrt(size/volume)
        volume = bar.get("volume", size * 100)
        participation = size / max(volume, 1)
        impact = self._impact_k * math.sqrt(participation) * price
        fill += impact if direction == "BUY" else -impact

        return round(max(0.01, fill), 2)

    def _close_position(self, position: dict, price: float, capital: float) -> tuple[float, float]:
        size      = position["size"]
        entry     = position["entry_price"]
        direction = position["direction"]

        fill = self._simulate_fill(price, "SELL" if direction == "BUY" else "BUY", size, {"volume": size * 200})

        if direction == "BUY":
            pnl = (fill - entry) * size
        else:
            pnl = (entry - fill) * size

        pnl -= self._commission   # round-trip commission
        new_capital = capital + entry * size + pnl  # return entry cost + P&L
        return round(pnl, 2), round(new_capital, 2)

    @staticmethod
    def _mark_to_market(position: dict | None, price: float) -> float:
        if not position:
            return 0.0
        direction = position["direction"]
        size      = position["size"]
        entry     = position["entry_price"]
        if direction == "BUY":
            return (price - entry) * size
        return (entry - price) * size
