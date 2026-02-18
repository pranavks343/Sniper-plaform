"""Circuit breaker for risk-based trading halt and resume."""
from __future__ import annotations

import hmac
from dataclasses import dataclass
from datetime import datetime


@dataclass
class BreakerStatus:
    active: bool
    reason: str | None
    timestamp: datetime | None
    actions_taken: list[str]


class CircuitBreaker:
    """Triggers on portfolio/market conditions and halts trading until admin resume."""

    def __init__(self, admin_secret: str = "") -> None:
        self._status = BreakerStatus(
            active=False, reason=None, timestamp=None, actions_taken=[]
        )
        self._admin_secret = admin_secret or ""

    def check_triggers(self, market_state: dict, portfolio_state: dict) -> bool:
        if abs(portfolio_state.get("daily_loss_pct", 0.0)) > portfolio_state.get(
            "max_daily_loss_pct", 0.02
        ):
            return True
        if abs(portfolio_state.get("drawdown_pct", 0.0)) > portfolio_state.get(
            "max_drawdown_pct", 0.10
        ):
            return True
        vix = market_state.get("vix", 20.0)
        vix_change = market_state.get("vix_change_pct", 0.0)
        latency_ms = market_state.get("latency_ms", 0.0)
        if vix > 40 or vix_change > 0.5 or latency_ms > 5000:
            return True
        return False

    def activate_breaker(self, reason: str) -> None:
        self._status = BreakerStatus(
            active=True,
            reason=reason,
            timestamp=datetime.utcnow(),
            actions_taken=[
                "cancel_pending_orders",
                "disable_new_orders",
                "snapshot_audit_state",
            ],
        )

    def deactivate_breaker(self, admin_password: str) -> None:
        if not self._admin_secret:
            raise ValueError(
                "circuit breaker admin secret not configured; set CIRCUIT_BREAKER_ADMIN_SECRET"
            )
        if not admin_password:
            raise ValueError("admin password required")
        if not hmac.compare_digest(self._admin_secret, admin_password):
            raise ValueError("invalid admin password")
        self._status = BreakerStatus(
            active=False,
            reason=None,
            timestamp=datetime.utcnow(),
            actions_taken=["resume_trading"],
        )

    def emergency_position_close(self) -> list[dict]:
        return [{"symbol": "ALL", "action": "CLOSE", "status": "queued"}]

    @property
    def status(self) -> BreakerStatus:
        return self._status
