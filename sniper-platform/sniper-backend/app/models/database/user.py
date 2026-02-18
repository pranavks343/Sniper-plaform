from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.database.base import Base
from app.models.database.namespaces import AUTH_SCHEMA


class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': AUTH_SCHEMA}

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), primary_key=True)
    clerk_user_id: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password_salt: Mapped[str | None] = mapped_column(String(64), nullable=True)
    role: Mapped[str] = mapped_column(String(32), nullable=False, server_default='trader')
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default='true')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    preferences: Mapped['UserPreference | None'] = relationship(
        'UserPreference',
        back_populates='user',
        uselist=False,
        cascade='all, delete-orphan',
    )
    broker_accounts: Mapped[list['BrokerAccount']] = relationship('BrokerAccount', back_populates='user')
    strategies: Mapped[list['Strategy']] = relationship('Strategy', back_populates='user')


class UserPreference(Base):
    __tablename__ = 'user_preferences'
    __table_args__ = {'schema': AUTH_SCHEMA}

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=False),
        ForeignKey(f'{AUTH_SCHEMA}.users.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,
        index=True,
    )
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, server_default='Asia/Kolkata')
    theme: Mapped[str] = mapped_column(String(16), nullable=False, server_default='dark')
    preferences_json: Mapped[str] = mapped_column(Text, nullable=False, server_default='{}')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped['User'] = relationship('User', back_populates='preferences')
