from sqlalchemy import Column, BigInteger, String, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.sql import func
from common.database import Base


class ActionPlan(Base):
    __tablename__ = "action_plans"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    last_trade_id = Column(BigInteger, ForeignKey("trades.id", ondelete="RESTRICT"), nullable=False)

    buy_title = Column(String(200), nullable=False)
    buy_summary = Column(String, nullable=False)
    buy_referenced_trade_ids = Column(JSON, nullable=False)

    sell_title = Column(String(200), nullable=False)
    sell_summary = Column(String, nullable=False)
    sell_referenced_trade_ids = Column(JSON, nullable=False)

    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)