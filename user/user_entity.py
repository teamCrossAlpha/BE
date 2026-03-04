from sqlalchemy import Column, BigInteger, String, TIMESTAMP, func
from common.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    email = Column(String(100))

    provider = Column(String(50), nullable=False)
    provider_id = Column(String(255), nullable=False)

    nickname = Column(String(100))
    profile_image = Column(String(500))

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )