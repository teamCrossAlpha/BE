from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from common.database import get_db
from common.dependencies import get_current_user_id

from .confidence_scatter_service import calculate_confidence_scatter
from .confidence_scatter_schema import ConfidenceScatterResponse

router = APIRouter(
    prefix="/api/insights/confidence/scatter",
    tags=["insights-confidence"],
)


@router.get("", response_model=ConfidenceScatterResponse)
def get_confidence_scatter(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return calculate_confidence_scatter(db, user_id)