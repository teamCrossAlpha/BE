from sqlalchemy import Column, BigInteger, ForeignKey, TIMESTAMP, func
from common.database import Base


class UserInterestSector(Base):
    __tablename__ = "user_interest_sectors"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    sector_id = Column(BigInteger, ForeignKey("sectors.id"))
    registered_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )
