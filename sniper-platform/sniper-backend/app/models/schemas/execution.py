from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.schemas.common import Direction, OrderStatus


class PlaceOrderRequest(BaseModel):
    symbol: str
    side: Direction
    quantity: int
    order_type: str = 'MARKET'
    price: float | None = None
    strategy_id: str | None = None
    urgency: float = 0.5


class OrderOut(BaseModel):
    id: str
    symbol: str
    side: Direction
    quantity: int
    order_type: str
    status: OrderStatus
    price: float | None = None
    filled_qty: int = 0
    avg_price: float | None = None
    strategy_id: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PositionOut(BaseModel):
    symbol: str
    quantity: int
    avg_price: float
    current_price: float
    pnl: float
    delta: float = 0.0
    gamma: float = 0.0
    theta: float = 0.0
    vega: float = 0.0


class TradeOut(BaseModel):
    id: str
    order_id: str
    symbol: str
    side: Direction
    quantity: int
    entry_price: float
    exit_price: float | None = None
    pnl: float = 0.0
    entry_time: datetime = Field(default_factory=datetime.utcnow)
    exit_time: datetime | None = None
