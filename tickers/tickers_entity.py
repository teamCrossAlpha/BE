from sqlalchemy import Column, BigInteger, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from common.database import Base


class Ticker(Base):
    __tablename__ = "tickers"

    id = Column(BigInteger, primary_key=True, index=True)

    sector_id = Column(BigInteger, ForeignKey("sectors.id", ondelete="CASCADE"), nullable=False)

    ticker = Column(String(10), nullable=False)
    company_name = Column(String(200), nullable=False)

    created_at = Column(DateTime, server_default=func.now())