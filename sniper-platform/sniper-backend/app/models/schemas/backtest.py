from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class BacktestCreate(BaseModel):
    strategy_id: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
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
