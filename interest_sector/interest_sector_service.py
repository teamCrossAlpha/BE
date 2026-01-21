from interest_sector.interest_sector_entity import UserInterestSector
from interest_sector.interest_sector_repository import save, delete
from sector.sector_repository import find_by_sector_key

def add_interest(db, user_id: int, sector_key: str):
    sector = find_by_sector_key(db, sector_key)

    entity = UserInterestSector(
        user_id=user_id,
        sector_id=sector.id
    )
    return save(db, entity)

def remove_interest(db, user_id: int, sector_key: str):
    sector = find_by_sector_key(db, sector_key)
    delete(db, user_id, sector.id)
