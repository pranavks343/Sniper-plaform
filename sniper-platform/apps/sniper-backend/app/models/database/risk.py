from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.database.base import Base
from app.models.database.namespaces import RISK_SCHEMA, STRATEGIES_SCHEMA


class RiskLimit(Base):
    __tablename__ = 'risk_limits'
    __table_args__ = {'schema': RISK_SCHEMA}

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), primary_key=True)
    user_id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), nullable=False, index=True)
    strategy_id: Mapped[str | None] = mapped_column(
        PGUUID(as_uuid=False),
        ForeignKey(f'{STRATEGIES_SCHEMA}.strategies.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
    )
    max_daily_loss_pct: Mapped[float] = mapped_column(Float, nullable=False, server_default='0.02')
    max_drawdown_pct: Mapped[float] = mapped_column(Float, nullable=False, server_default='0.10')
    max_delta: Mapped[float] = mapped_column(Float, nullable=False, server_default='500')
    max_gamma: Mapped[float] = mapped_column(Float, nullable=False, server_default='50')
    max_vega: Mapped[float] = mapped_column(Float, nullable=False, server_default='10000')
    updated_by: Mapped[str] = mapped_column(String(64), nullable=False, server_default='system')
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class RiskBreach(Base):
    __tablename__ = 'risk_breaches'
    __table_args__ = {'schema': RISK_SCHEMA}

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), primary_key=True)
    user_id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), nullable=False, index=True)
    strategy_id: Mapped[str | None] = mapped_column(
        PGUUID(as_uuid=False),
        ForeignKey(f'{STRATEGIES_SCHEMA}.strategies.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
    )
    type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(32), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    limit: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    action_taken: Mapped[str | None] = mapped_column(String(128), nullable=True)
    details: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


class CircuitBreakerEvent(Base):
    __tablename__ = 'circuit_breaker_events'
    __table_args__ = {'schema': RISK_SCHEMA}

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), primary_key=True)
    user_id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), nullable=False, index=True)
    strategy_id: Mapped[str | None] = mapped_column(
        PGUUID(as_uuid=False),
        ForeignKey(f'{STRATEGIES_SCHEMA}.strategies.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    actor: Mapped[str] = mapped_column(String(64), nullable=False, server_default='system')
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
