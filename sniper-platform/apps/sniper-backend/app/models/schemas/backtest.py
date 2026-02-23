from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class BacktestCreate(BaseModel):
    strategy_id: str | None = None
    symbol: str = 'NIFTY'
    strategy_type: str = 'momentum'
    start_date: datetime | None = None
    end_date: datetime | None = None
    initial_capital: float = 1_000_000.0
    transaction_cost_model: str = 'realistic'


class BacktestStatus(BaseModel):
    job_id: str
    status: str
    progress: float


class BacktestResult(BaseModel):
    job_id: str
    metrics: dict
    equity_curve: list[dict]
    trades: list[dict]
    drawdowns: list[dict]
