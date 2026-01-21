from fastapi import APIRouter, Depends
from common.database import get_db
from common.dependencies import get_current_user_id
from interest_sector.interest_sector_schema import InterestSectorRequest
from interest_sector.interest_sector_service import add_interest, remove_interest


router = APIRouter(prefix="/api/users/me")

@router.post("/interest-sectors")
def add_interest_sector(
    body: InterestSectorRequest,
    db = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    entity = add_interest(db, user_id, body.sectorKey)
    return [{
        "sectorKey": body.sectorKey,
        "registeredAt": entity.registered_at
    }]

@router.delete("/interest-sectors/{sector_key}")
def delete_interest_sector(
    sector_key: str,
    db = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    remove_interest(db, user_id, sector_key)
    return {"message": "deleted"}
