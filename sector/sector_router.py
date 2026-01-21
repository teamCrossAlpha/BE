from fastapi import APIRouter, Depends
from common.database import get_db
from common.dependencies import get_current_user_id
from sector.service.sector_service import get_sector_overview

router = APIRouter(prefix="/api")


@router.get("/sector-overview")
def sector_overview(
    db=Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    sectors = get_sector_overview(db, user_id)
    return {
        "count": len(sectors),
        "sectors": sectors,
    }
