from sqlalchemy import (
    Column, BigInteger, String, Date,
    JSON, ForeignKey, TIMESTAMP, func
)
from common.database import Base


class SectorSummary(Base):
    __tablename__ = "sector_summaries"

    id = Column(BigInteger, primary_key=True)
    sector_id = Column(BigInteger, ForeignKey("sectors.id"), nullable=False)

    title = Column(String(200), nullable=False)
    summary_date = Column(Date, nullable=False)

    preview = Column(String(400), nullable=False)
    content = Column(String, nullable=False)

    key_points = Column(JSON, nullable=False)
    sources = Column(JSON, nullable=False)

    created_at = Column(TIMESTAMP, server_default=func.now())
