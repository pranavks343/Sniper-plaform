"""
State Manager — Position/Order/Strategy persistence + crash recovery.

Persists the entire trading state to a JSON snapshot file.
On startup, if a snapshot exists and is <5 minutes old, it is loaded
automatically (crash recovery).

State includes:
  - Open positions (symbol → {qty, avg_price, side})
  - Pending/open orders (order_id → order_dict)
  - Active strategies (strategy_id → config)
  - P&L history (list of daily snapshots)
  - Circuit breaker status
"""
from __future__ import annotations

import json
import logging
import os
import threading
import time
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("sniper.state")


@dataclass
class TradingState:
    positions:        dict[str, dict]   = field(default_factory=dict)
    orders:           dict[str, dict]   = field(default_factory=dict)
    strategies:       dict[str, dict]   = field(default_factory=dict)
    pnl_history:      list[dict]        = field(default_factory=list)
    breaker_active:   bool              = False
    snapshot_ts:      str               = ""
    session_start_ts: str               = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "TradingState":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


class StateManager:
    """
    Thread-safe state store with:
    - In-memory state (fast access)
    - Periodic JSON snapshot (every 30s by default)
    - Crash recovery on startup
    - Atomic writes (write-then-rename)
    """

    SNAPSHOT_MAX_AGE_S = 300   # 5 minutes — older snapshots are stale

    def __init__(
        self,
        snapshot_path: str = "/tmp/sniper_state.json",
        flush_interval_s: float = 30.0,
    ) -> None:
        self._path = Path(snapshot_path)
        self._flush_interval = flush_interval_s
        self._lock = threading.RLock()
        self._state = TradingState(session_start_ts=datetime.now(timezone.utc).isoformat())
        self._dirty = False
        self._stop_event = threading.Event()
        self._flusher: threading.Thread | None = None

        self._try_recover()

    # ------------------------------------------------------------------
    # Positions
    # ------------------------------------------------------------------

    def upsert_position(self, symbol: str, qty: int, avg_price: float, side: str) -> None:
        with self._lock:
            self._state.positions[symbol] = {
                "qty": qty, "avg_price": avg_price, "side": side,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            self._dirty = True

    def remove_position(self, symbol: str) -> None:
        with self._lock:
            self._state.positions.pop(symbol, None)
            self._dirty = True

    def get_positions(self) -> dict[str, dict]:
        with self._lock:
            return deepcopy(self._state.positions)

    # ------------------------------------------------------------------
    # Orders
    # ------------------------------------------------------------------

    def save_order(self, order_id: str, order: dict) -> None:
        with self._lock:
            self._state.orders[order_id] = {**order, "saved_at": datetime.now(timezone.utc).isoformat()}
            self._dirty = True

    def update_order_status(self, order_id: str, status: str, **kwargs: Any) -> None:
        with self._lock:
            if order_id in self._state.orders:
                self._state.orders[order_id]["status"] = status
                self._state.orders[order_id].update(kwargs)
                self._dirty = True

    def get_open_orders(self) -> dict[str, dict]:
        with self._lock:
            return {oid: deepcopy(o) for oid, o in self._state.orders.items()
                    if o.get("status") in ("PENDING", "PARTIAL")}

    # ------------------------------------------------------------------
    # Strategies
    # ------------------------------------------------------------------

    def save_strategy(self, strategy_id: str, config: dict) -> None:
        with self._lock:
            self._state.strategies[strategy_id] = {**config, "saved_at": datetime.now(timezone.utc).isoformat()}
            self._dirty = True

    def remove_strategy(self, strategy_id: str) -> None:
        with self._lock:
            self._state.strategies.pop(strategy_id, None)
            self._dirty = True

    def get_active_strategies(self) -> dict[str, dict]:
        with self._lock:
            return {sid: deepcopy(s) for sid, s in self._state.strategies.items()
                    if s.get("status") == "active"}

    # ------------------------------------------------------------------
    # P&L
    # ------------------------------------------------------------------

    def record_pnl_snapshot(self, realized: float, unrealized: float, equity: float) -> None:
        with self._lock:
            self._state.pnl_history.append({
                "ts":         datetime.now(timezone.utc).isoformat(),
                "realized":   realized,
                "unrealized": unrealized,
                "equity":     equity,
            })
            # Keep last 500 snapshots
            if len(self._state.pnl_history) > 500:
                self._state.pnl_history = self._state.pnl_history[-500:]
            self._dirty = True

    # ------------------------------------------------------------------
    # Circuit breaker
    # ------------------------------------------------------------------

    def set_breaker(self, active: bool) -> None:
        with self._lock:
            self._state.breaker_active = active
            self._dirty = True

    def is_breaker_active(self) -> bool:
        with self._lock:
            return self._state.breaker_active

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def flush(self) -> None:
        """Atomic write of current state to disk."""
        with self._lock:
            if not self._dirty:
                return
            self._state.snapshot_ts = datetime.now(timezone.utc).isoformat()
            data = self._state.to_dict()

        tmp = self._path.with_suffix(".tmp")
        try:
            tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
            tmp.replace(self._path)     # atomic rename
            self._dirty = False
            logger.debug("State flushed → %s", self._path)
        except Exception as exc:
            logger.error("State flush failed: %s", exc)

    def start_background_flush(self) -> None:
        """Start background thread that flushes every flush_interval_s."""
        self._stop_event.clear()
        self._flusher = threading.Thread(target=self._flush_loop, daemon=True, name="state-flusher")
        self._flusher.start()

    def stop_background_flush(self) -> None:
        self._stop_event.set()
        self.flush()    # final flush on shutdown

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _flush_loop(self) -> None:
        while not self._stop_event.wait(timeout=self._flush_interval):
            self.flush()

    def _try_recover(self) -> None:
        """Load snapshot if it exists and is fresh enough."""
        if not self._path.exists():
            logger.info("No snapshot found — starting fresh")
            return
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            ts_str = data.get("snapshot_ts", "")
            if ts_str:
                ts = datetime.fromisoformat(ts_str)
                age_s = (datetime.now(timezone.utc) - ts.replace(tzinfo=timezone.utc)).total_seconds()
                if age_s > self.SNAPSHOT_MAX_AGE_S:
                    logger.warning("Snapshot is %.0fs old — too stale, ignoring", age_s)
                    return
            self._state = TradingState.from_dict(data)
            logger.info(
                "Crash recovery: loaded %d positions, %d orders, %d strategies",
                len(self._state.positions),
                len(self._state.orders),
                len(self._state.strategies),
            )
        except Exception as exc:
            logger.error("Snapshot load failed: %s — starting fresh", exc)
