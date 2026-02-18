from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.database.base import Base
from app.models.database.namespaces import ANALYTICS_SCHEMA


class QuantumUsage(Base):
    __tablename__ = 'quantum_usage'
    __table_args__ = {'schema': ANALYTICS_SCHEMA}

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    optimization_type: Mapped[str] = mapped_column(String(64), nullable=False)
    solve_time: Mapped[float] = mapped_column(Float, nullable=False)
    cost: Mapped[float] = mapped_column(Float, nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
