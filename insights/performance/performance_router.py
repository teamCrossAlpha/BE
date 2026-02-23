from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from common.database import get_db
from common.dependencies import get_current_user_id

from .performance_service import calculate_performance_score
from .performance_schema import PerformanceScoreResponse

router = APIRouter(prefix="/api/insights/performance", tags=["insights-performance"])


@router.get("", response_model=PerformanceScoreResponse)
def get_performance_score(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return calculate_performance_score(db, user_id)