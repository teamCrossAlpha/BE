from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from common.database import get_db
from common.dependencies import get_current_user_id

from .sell_service import calculate_sell_pattern
from .sell_schema import SellPatternResponse

router = APIRouter(
    prefix="/api/insights/sell-pattern",
    tags=["insights-sell-pattern"],
)


@router.get("", response_model=SellPatternResponse)
def get_sell_pattern(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return calculate_sell_pattern(db, user_id)