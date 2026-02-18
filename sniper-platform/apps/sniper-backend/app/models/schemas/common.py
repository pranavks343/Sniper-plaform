from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Direction(str, Enum):
    BUY = 'BUY'
    SELL = 'SELL'


class Regime(str, Enum):
    TRENDING = 'TRENDING'
    MEAN_REVERTING = 'MEAN_REVERTING'
    VOLATILE = 'VOLATILE'


class OrderStatus(str, Enum):
    PENDING = 'PENDING'
    PARTIAL = 'PARTIAL'
    COMPLETE = 'COMPLETE'
    CANCELLED = 'CANCELLED'


class BaseResponse(BaseModel):
    success: bool = True
    message: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
