"""
Main Trading Loop
tick → bar → signal → meta-label → position-size → execute → risk-check → order

Orchestrates all framework components into a single async trading session.
"""
from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

logger = logging.getLogger("sniper.orchestration.loop")


class TradingLoop:
    """
    Async main loop that wires together:
      - Data pipeline (bar aggregator)
      - Strategy engine (regime + signal + meta-label + position-size)
      - Execution engine (PPO agent + smart router)
      - Risk engine (limit monitor + circuit breaker)
      - Broker adapter
      - Event bus
      - State manager
    """

    def __init__(
        self,
        broker:           Any,
        bar_aggregator:   Any,
        regime_detector:  Any,
        signal_generator: Any,
        meta_labeler:     Any,
        position_sizer:   Any,
        ppo_agent:        Any,
        order_router:     Any,
        limit_monitor:    Any,
        circuit_breaker:  Any,
        state_manager:    Any,
        event_bus:        Any,
        strategy_lifecycle: Any,
    ) -> None:
        self._broker         = broker
        self._bar_agg        = bar_aggregator
        self._regime         = regime_detector
        self._signal         = signal_generator
        self._meta           = meta_labeler
        self._sizer          = position_sizer
        self._ppo            = ppo_agent
        self._router         = order_router
        self._limits         = limit_monitor
        self._breaker        = circuit_breaker
        self._state          = state_manager
        self._bus            = event_bus
        self._lifecycle      = strategy_lifecycle
        self._running        = False
        self._bar_buffer:    dict[str, list[dict]] = {}   # symbol → bars

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Start the trading loop and begin processing events."""
        self._running = True
        self._state.start_background_flush()
        logger.info("Trading loop started")
        await asyncio.gather(
            self._bus.run(),
            self._heartbeat(),
        )

    async def stop(self) -> None:
        """Graceful shutdown: cancel orders → close positions → save state."""
        logger.info("Initiating graceful shutdown...")
        self._running = False

        # 1. Cancel all pending orders
        open_orders = self._state.get_open_orders()
        for order_id in open_orders:
            try:
                self._broker.cancel_order(order_id)
                self._state.update_order_status(order_id, "CANCELLED")
                logger.info("Cancelled order %s", order_id)
            except Exception as exc:
                logger.error("Failed to cancel order %s: %s", order_id, exc)

        # 2. Close all open positions
        positions = self._state.get_positions()
        for symbol, pos in positions.items():
            try:
                side = "SELL" if pos["side"] == "BUY" else "BUY"
                order_id = self._broker.place_order(
                    symbol=symbol,
                    quantity=abs(pos["qty"]),
                    order_type="MARKET",
                    price=0,
                    side=side,
                )
                self._state.remove_position(symbol)
                logger.info("Closed position %s (order %s)", symbol, order_id)
            except Exception as exc:
                logger.error("Failed to close position %s: %s", symbol, exc)

        # 3. Final state flush
        self._state.stop_background_flush()
        await self._bus.stop()
        logger.info("Graceful shutdown complete")

    # ------------------------------------------------------------------
    # Core pipeline — called per bar close
    # ------------------------------------------------------------------

    async def on_bar(self, bar: Any) -> None:
        """
        Main pipeline: bar → regime → signal → meta → size → execute → risk
        Called by BarAggregator callback on every closed bar.
        """
        if not self._running:
            return

        symbol = bar.symbol
        if symbol not in self._bar_buffer:
            self._bar_buffer[symbol] = []

        self._bar_buffer[symbol].append({
            "open": bar.open, "high": bar.high, "low": bar.low,
            "close": bar.close, "volume": bar.volume, "ts": bar.ts_open,
        })

        bars = self._bar_buffer[symbol]
        if len(bars) < 60:
            return   # not enough data yet

        prices = [b["close"] for b in bars]

        # ── 1. Regime detection ──────────────────────────────────────
        regime_state = self._regime.predict_regime(prices)
        regime       = regime_state.regime

        # ── 2. Signal generation ─────────────────────────────────────
        signals = self._signal.generate_signals(bars, regime)
        if not signals:
            return

        for signal in signals:
            # ── 3. Meta-labeling ─────────────────────────────────────
            meta_features = self._build_meta_features(bars, regime_state)
            meta = self._meta.predict(meta_features)
            if not meta.primary_signal:
                logger.debug("Meta-labeler filtered signal for %s", symbol)
                continue

            # ── 4. Position sizing ────────────────────────────────────
            stop_loss = bar.close * (0.985 if signal.direction.value == "BUY" else 1.015)
            size_result = self._sizer.compute(
                capital=self._get_capital(),
                entry_price=bar.close,
                stop_loss_price=stop_loss,
                win_rate=0.55,
                avg_win=bar.close * 0.01,
                avg_loss=bar.close * 0.007,
                regime=regime,
            )

            if size_result.quantity <= 0:
                logger.debug("Position sizer returned 0 qty for %s", symbol)
                continue

            # ── 5. Risk pre-trade check ───────────────────────────────
            risk_status = self._limits.check_pre_trade(
                new_position={"symbol": symbol, "qty": size_result.quantity, "price": bar.close},
                current_portfolio=self._state.get_positions(),
            )
            if not risk_status:
                logger.info("Pre-trade risk rejected %s", symbol)
                continue

            # ── 6. Circuit breaker ────────────────────────────────────
            if self._breaker.status.active:
                logger.warning("Circuit breaker active — skipping order for %s", symbol)
                continue

            # ── 7. PPO execution decision ─────────────────────────────
            market_state = {"spread_bps": 8, "volatility_1m": 0.5, "trend": 0.0}
            exec_action  = self._ppo.decide(
                order={"quantity": size_result.quantity, "urgency": 0.5},
                market_state=market_state,
                regime_code=["TRENDING", "MEAN_REVERTING", "VOLATILE"].index(regime.value),
            )

            # ── 8. QAOA order routing ─────────────────────────────────
            route = self._router.route(
                order={"symbol": symbol, "quantity": size_result.quantity,
                       "side": signal.direction.value, "urgency": 0.5},
            )

            # ── 9. Place order ────────────────────────────────────────
            await asyncio.sleep(exec_action.delay_ms / 1000)
            try:
                order_id = self._broker.place_order(
                    symbol=symbol,
                    quantity=size_result.quantity,
                    order_type=exec_action.order_type,
                    price=bar.close,
                    side=signal.direction.value,
                )
                self._state.save_order(order_id, {
                    "symbol": symbol, "qty": size_result.quantity,
                    "side": signal.direction.value, "status": "PENDING",
                    "price": bar.close,
                })
                logger.info(
                    "Order placed: %s %s %d %s @ %.2f (regime=%s confidence=%.2f)",
                    order_id, signal.direction.value, size_result.quantity,
                    symbol, bar.close, regime.value, meta.confidence,
                )
            except Exception as exc:
                logger.error("Order placement failed for %s: %s", symbol, exc)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _heartbeat(self) -> None:
        while self._running:
            await asyncio.sleep(60)
            positions = self._state.get_positions()
            logger.info("Heartbeat — positions: %d, loop: RUNNING", len(positions))

    def _get_capital(self) -> float:
        try:
            margins = self._broker.get_margins()
            return float(margins.get("available", 1_000_000))
        except Exception:
            return 1_000_000.0

    @staticmethod
    def _build_meta_features(bars: list[dict], regime_state: Any) -> dict[str, float]:
        closes = [b["close"] for b in bars[-20:]]
        if len(closes) < 2:
            return {}
        returns = [(closes[i] - closes[i - 1]) / closes[i - 1] for i in range(1, len(closes))]
        avg_vol = sum(b.get("volume", 0) for b in bars[-5:]) / 5
        cur_vol = bars[-1].get("volume", avg_vol)
        return {
            "rsi":              50.0,   # simplified
            "macd_hist":        returns[-1] * 100,
            "ema_spread_pct":   (closes[-1] - closes[0]) / closes[0] * 100,
            "vol_ratio":        cur_vol / max(avg_vol, 1),
            "regime_confidence": regime_state.confidence,
            "win_streak":       0.0,
            "loss_streak":      0.0,
            "atr_pct":          max(abs(r) for r in returns) * 100,
        }
