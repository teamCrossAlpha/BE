from sqlalchemy.orm import Session
from sector.sector_entity import Sector


def find_all(db: Session):
    return db.query(Sector).all()


def find_by_sector_key(db: Session, sector_key: str):
    return (
        db.query(Sector)
        .filter(Sector.sector_key == sector_key)
        .first()
    )
