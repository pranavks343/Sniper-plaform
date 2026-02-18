from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.database.base import Base
from app.models.database.namespaces import BACKTEST_SCHEMA, STRATEGIES_SCHEMA


class BacktestRun(Base):
    __tablename__ = 'backtest_runs'
    __table_args__ = {'schema': BACKTEST_SCHEMA}

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), primary_key=True)
    strategy_id: Mapped[str | None] = mapped_column(
        PGUUID(as_uuid=False),
        ForeignKey(f'{STRATEGIES_SCHEMA}.strategies.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
    )
    user_id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default='queued', index=True)
    progress: Mapped[float] = mapped_column(Float, nullable=False, server_default='0')
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    initial_capital: Mapped[float] = mapped_column(Float, nullable=False)
    final_capital: Mapped[float] = mapped_column(Float, nullable=False, server_default='0')
    transaction_cost_model: Mapped[str] = mapped_column(String(64), nullable=False, server_default='realistic')
    config: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    metrics: Mapped[list['BacktestMetric']] = relationship(
        'BacktestMetric',
        back_populates='run',
        cascade='all, delete-orphan',
    )
    trades: Mapped[list['BacktestTrade']] = relationship(
        'BacktestTrade',
        back_populates='run',
        cascade='all, delete-orphan',
    )


class BacktestMetric(Base):
    __tablename__ = 'backtest_metrics'
    __table_args__ = {'schema': BACKTEST_SCHEMA}

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), primary_key=True)
    run_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=False),
        ForeignKey(f'{BACKTEST_SCHEMA}.backtest_runs.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    metric_name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    run: Mapped['BacktestRun'] = relationship('BacktestRun', back_populates='metrics')


class BacktestTrade(Base):
    __tablename__ = 'backtest_trades'
    __table_args__ = {'schema': BACKTEST_SCHEMA}

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), primary_key=True)
    run_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=False),
        ForeignKey(f'{BACKTEST_SCHEMA}.backtest_runs.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    side: Mapped[str] = mapped_column(String(8), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    entry_price: Mapped[float] = mapped_column(Float, nullable=False)
    exit_price: Mapped[float] = mapped_column(Float, nullable=False)
    pnl: Mapped[float] = mapped_column(Float, nullable=False)
    trade_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    run: Mapped['BacktestRun'] = relationship('BacktestRun', back_populates='trades')
