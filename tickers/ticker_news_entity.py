from sqlalchemy import Column, BigInteger, String, Text, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from common.database import Base


class TickerNews(Base):
    __tablename__ = "ticker_news"

    id = Column(BigInteger, primary_key=True, index=True)

    ticker_id = Column(BigInteger, ForeignKey("tickers.id", ondelete="CASCADE"), nullable=False)

    article_id = Column(String(200), nullable=False)
    title = Column(Text, nullable=False)
    summary = Column(Text)
    source = Column(String(100))
    url = Column(Text)
    published_at = Column(DateTime)

    snapshot_date = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("ticker_id", "article_id", name="uq_ticker_article"),
    )