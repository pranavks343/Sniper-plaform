"""
Strategy Lifecycle Manager
Manages create → activate → pause → stop → delete transitions.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("sniper.orchestration.lifecycle")

VALID_TRANSITIONS: dict[str, list[str]] = {
    "created":   ["active", "deleted"],
    "active":    ["paused", "stopped", "deleted"],
    "paused":    ["active", "stopped", "deleted"],
    "stopped":   ["active", "deleted"],
    "deleted":   [],
}


class StrategyLifecycle:
    """
    In-memory strategy registry with state machine enforcement.
    Pairs with StateManager for persistence.
    """

    def __init__(self) -> None:
        self._strategies: dict[str, dict[str, Any]] = {}

    # ------------------------------------------------------------------

    def create(self, config: dict) -> str:
        """Register a new strategy. Returns strategy_id."""
        sid = str(uuid.uuid4())
        self._strategies[sid] = {
            "id":         sid,
            "status":     "created",
            "config":     config,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "stats":      {"signals": 0, "orders": 0, "fills": 0},
        }
        logger.info("Strategy created: %s (%s)", sid[:8], config.get("name", "?"))
        return sid

    def activate(self, strategy_id: str) -> bool:
        return self._transition(strategy_id, "active")

    def pause(self, strategy_id: str) -> bool:
        return self._transition(strategy_id, "paused")

    def stop(self, strategy_id: str) -> bool:
        return self._transition(strategy_id, "stopped")

    def delete(self, strategy_id: str) -> bool:
        ok = self._transition(strategy_id, "deleted")
        if ok:
            del self._strategies[strategy_id]
        return ok

    def increment_stat(self, strategy_id: str, field: str, n: int = 1) -> None:
        if strategy_id in self._strategies:
            self._strategies[strategy_id]["stats"][field] = \
                self._strategies[strategy_id]["stats"].get(field, 0) + n

    def get(self, strategy_id: str) -> dict | None:
        return self._strategies.get(strategy_id)

    def list_active(self) -> list[dict]:
        return [s for s in self._strategies.values() if s["status"] == "active"]

    def all(self) -> list[dict]:
        return list(self._strategies.values())

    # ------------------------------------------------------------------

    def _transition(self, sid: str, target: str) -> bool:
        if sid not in self._strategies:
            logger.error("Strategy %s not found", sid)
            return False
        current = self._strategies[sid]["status"]
        allowed = VALID_TRANSITIONS.get(current, [])
        if target not in allowed:
            logger.warning("Invalid transition %s → %s for strategy %s", current, target, sid[:8])
            return False
        self._strategies[sid]["status"]     = target
        self._strategies[sid]["updated_at"] = datetime.now(timezone.utc).isoformat()
        logger.info("Strategy %s: %s → %s", sid[:8], current, target)
        return True
