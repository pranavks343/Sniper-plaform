from __future__ import annotations

from pydantic import BaseModel


class QuantumStatus(BaseModel):
    available: bool
    provider: str
    backend: str
    credits: float
    last_solve: str | None


class QuantumConfigUpdate(BaseModel):
    enable_quantum_routing: bool | None = None
    enable_quantum_portfolio: bool | None = None
    enable_quantum_hedging: bool | None = None
    quantum_timeout_ms: int | None = None


class QuantumConnectPayload(BaseModel):
    api_token: str | None = None


class QuantumUsageStats(BaseModel):
    total_solves: int
    avg_solve_time_ms: float
    cost_this_month: float
