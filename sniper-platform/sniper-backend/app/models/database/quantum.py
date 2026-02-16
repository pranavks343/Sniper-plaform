from sqlalchemy import Boolean, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.database.base import Base


class QuantumUsage(Base):
    __tablename__ = 'quantum_usage'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    timestamp: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    optimization_type: Mapped[str] = mapped_column(String(64), nullable=False)
    solve_time: Mapped[float] = mapped_column(Float, nullable=False)
    cost: Mapped[float] = mapped_column(Float, nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
