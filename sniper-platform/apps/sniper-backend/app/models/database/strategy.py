from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.database.base import Base
from app.models.database.namespaces import AUTH_SCHEMA, STRATEGIES_SCHEMA


class Strategy(Base):
    __tablename__ = 'strategies'
    __table_args__ = {'schema': STRATEGIES_SCHEMA}

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=False),
        ForeignKey(f'{AUTH_SCHEMA}.users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    type: Mapped[str] = mapped_column(String(64), nullable=False)
    parameters: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    regime_filters: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default='inactive')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped['User'] = relationship('User', back_populates='strategies')
    versions: Mapped[list['StrategyVersion']] = relationship(
        'StrategyVersion',
        back_populates='strategy',
        cascade='all, delete-orphan',
    )


class StrategyVersion(Base):
    __tablename__ = 'strategy_versions'
    __table_args__ = (
        UniqueConstraint('strategy_id', 'version', name='uq_strategy_versions_strategy_id_version'),
        {'schema': STRATEGIES_SCHEMA},
    )

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), primary_key=True)
    strategy_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=False),
        ForeignKey(f'{STRATEGIES_SCHEMA}.strategies.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    parameters: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    changed_by: Mapped[str] = mapped_column(String(64), nullable=False, server_default='system')
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    strategy: Mapped['Strategy'] = relationship('Strategy', back_populates='versions')
