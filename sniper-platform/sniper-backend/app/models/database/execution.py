from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, JSON, PrimaryKeyConstraint, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.database.base import Base
from app.models.database.namespaces import (
    ANALYTICS_SCHEMA,
    AUTH_SCHEMA,
    BROKERS_SCHEMA,
    PORTFOLIO_SCHEMA,
    STRATEGIES_SCHEMA,
    TRADING_SCHEMA,
)


class BrokerAccount(Base):
    __tablename__ = 'broker_accounts'
    __table_args__ = (
        UniqueConstraint('user_id', 'provider', 'account_id', name='uq_broker_accounts_user_provider_account'),
        {'schema': BROKERS_SCHEMA},
    )

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=False),
        ForeignKey(f'{AUTH_SCHEMA}.users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    provider: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    account_id: Mapped[str] = mapped_column(String(128), nullable=False)
    encrypted_credentials: Mapped[str] = mapped_column(Text, nullable=False)
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default='true')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped['User'] = relationship('User', back_populates='broker_accounts')


class Order(Base):
    __tablename__ = 'orders'
    __table_args__ = {'schema': TRADING_SCHEMA}

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), primary_key=True)
    user_id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), nullable=False, index=True)
    strategy_id: Mapped[str | None] = mapped_column(
        PGUUID(as_uuid=False),
        ForeignKey(f'{STRATEGIES_SCHEMA}.strategies.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
    )
    broker_account_id: Mapped[str | None] = mapped_column(
        PGUUID(as_uuid=False),
        ForeignKey(f'{BROKERS_SCHEMA}.broker_accounts.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
    )
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    side: Mapped[str] = mapped_column(String(8), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    order_type: Mapped[str] = mapped_column(String(16), nullable=False)
    price: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, server_default='PENDING', index=True)
    filled_qty: Mapped[int] = mapped_column(Integer, nullable=False, server_default='0')
    avg_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    routing_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    cost_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    events: Mapped[list['OrderEvent']] = relationship(
        'OrderEvent',
        back_populates='order',
        cascade='all, delete-orphan',
    )
    trades: Mapped[list['Trade']] = relationship(
        'Trade',
        back_populates='order',
        cascade='all, delete-orphan',
    )


class OrderEvent(Base):
    __tablename__ = 'order_events'
    __table_args__ = {'schema': TRADING_SCHEMA}

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), primary_key=True)
    order_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=False),
        ForeignKey(f'{TRADING_SCHEMA}.orders.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    order: Mapped['Order'] = relationship('Order', back_populates='events')


class Trade(Base):
    __tablename__ = 'trades'
    __table_args__ = {'schema': TRADING_SCHEMA}

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), primary_key=True)
    user_id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), nullable=False, index=True)
    order_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=False),
        ForeignKey(f'{TRADING_SCHEMA}.orders.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    side: Mapped[str] = mapped_column(String(8), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    entry_price: Mapped[float] = mapped_column(Float, nullable=False)
    exit_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    fees: Mapped[float] = mapped_column(Float, nullable=False, server_default='0')
    pnl: Mapped[float] = mapped_column(Float, nullable=False, server_default='0')
    entry_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    exit_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    order: Mapped['Order'] = relationship('Order', back_populates='trades')


class PositionSnapshot(Base):
    __tablename__ = 'position_snapshots'
    __table_args__ = (
        PrimaryKeyConstraint('id', 'as_of'),
        {'schema': PORTFOLIO_SCHEMA},
    )

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=False))
    user_id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), nullable=False, index=True)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_price: Mapped[float] = mapped_column(Float, nullable=False)
    current_price: Mapped[float] = mapped_column(Float, nullable=False)
    pnl: Mapped[float] = mapped_column(Float, nullable=False, server_default='0')
    delta: Mapped[float] = mapped_column(Float, nullable=False, server_default='0')
    gamma: Mapped[float] = mapped_column(Float, nullable=False, server_default='0')
    theta: Mapped[float] = mapped_column(Float, nullable=False, server_default='0')
    vega: Mapped[float] = mapped_column(Float, nullable=False, server_default='0')
    as_of: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    is_eod: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default='false')


class PnlDaily(Base):
    __tablename__ = 'pnl_daily'
    __table_args__ = {'schema': ANALYTICS_SCHEMA}

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), primary_key=True)
    user_id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), nullable=False, index=True)
    trade_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    realized_pnl: Mapped[float] = mapped_column(Float, nullable=False, server_default='0')
    unrealized_pnl: Mapped[float] = mapped_column(Float, nullable=False, server_default='0')
    gross_pnl: Mapped[float] = mapped_column(Float, nullable=False, server_default='0')
    net_pnl: Mapped[float] = mapped_column(Float, nullable=False, server_default='0')
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class PnlIntraday(Base):
    __tablename__ = 'pnl_intraday'
    __table_args__ = (
        PrimaryKeyConstraint('id', 'as_of'),
        {'schema': ANALYTICS_SCHEMA},
    )

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=False))
    user_id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), nullable=False, index=True)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    as_of: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    realized_pnl: Mapped[float] = mapped_column(Float, nullable=False, server_default='0')
    unrealized_pnl: Mapped[float] = mapped_column(Float, nullable=False, server_default='0')
    net_pnl: Mapped[float] = mapped_column(Float, nullable=False, server_default='0')
