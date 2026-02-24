from __future__ import annotations

from sqlalchemy import Column, BigInteger, Date, Numeric, DateTime, ForeignKey, UniqueConstraint, CheckConstraint, func
from common.database import Base


class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"
    __table_args__ = (
        UniqueConstraint("user_id", "captured_date", name="uq_portfolio_user_date"),
        CheckConstraint("total_value >= 0", name="chk_total_value"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    captured_date = Column(Date, nullable=False)

    total_value = Column(Numeric(18, 4), nullable=False)
    total_profit_rate = Column(Numeric(10, 6), nullable=True)
    total_profit_amount = Column(Numeric(18, 4), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)