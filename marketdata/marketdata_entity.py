from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, func
from common.database import Base


class AssetPrice(Base):
    __tablename__ = "asset_prices"

    ticker = Column(String(16), primary_key=True) 
    price = Column(Numeric(18, 6), nullable=False)
    change = Column(Numeric(18, 6), nullable=True)
    change_rate = Column(Numeric(18, 8), nullable=True)

    captured_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())