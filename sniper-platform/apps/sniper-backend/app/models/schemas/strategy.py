from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.schemas.common import Regime


class StrategyCreate(BaseModel):
    name: str
    type: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    regime_filters: list[Regime] = Field(default_factory=list)


class StrategyUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    parameters: dict[str, Any] | None = None
    status: str | None = None


class StrategyOut(BaseModel):
    id: str
    user_id: str
    name: str
    type: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    status: str = 'inactive'
    regime_filters: list[Regime] = Field(default_factory=list)
    created_at: datetime
