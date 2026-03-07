from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from common.database import get_db
from common.dependencies import get_current_user_id

from .confidence_range_service import calculate_confidence_range
from .confidence_range_schema import ConfidenceRangeResponse

router = APIRouter(
    prefix="/api/insights/confidence/range",
    tags=["insights-confidence"],
)


@router.get("", response_model=ConfidenceRangeResponse)
def get_confidence_range(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return calculate_confidence_range(db, user_id)