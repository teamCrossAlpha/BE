from sqlalchemy.orm import Session
from interest_sector.interest_sector_entity import UserInterestSector

def find_by_user(db: Session, user_id: int):
    return db.query(UserInterestSector)\
        .filter(UserInterestSector.user_id == user_id)\
        .all()

def save(db: Session, entity):
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity

def delete(db: Session, user_id: int, sector_id: int):
    db.query(UserInterestSector)\
        .filter(
            UserInterestSector.user_id == user_id,
            UserInterestSector.sector_id == sector_id
        ).delete()
    db.commit()

