from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class RiskLimits(BaseModel):
    max_daily_loss_pct: float = 0.02
    max_drawdown_pct: float = 0.10
    max_delta: float = 500.0
    max_gamma: float = 50.0
    max_vega: float = 10000.0


class RiskViolation(BaseModel):
    type: str
    severity: str
    value: float
    limit: float
    action_taken: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class RiskMetrics(BaseModel):
    daily_pnl: float
    drawdown: float
    delta: float
    gamma: float
    vega: float
    trading_allowed: bool


class PortfolioStateUpdate(BaseModel):
    delta: float = 0.0
    gamma: float = 0.0
    theta: float = 0.0
    vega: float = 0.0


class CircuitBreakerRequest(BaseModel):
    reason: str


class CircuitBreakerDeactivateRequest(BaseModel):
    admin_password: str
