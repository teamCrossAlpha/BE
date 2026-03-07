from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from common.database import get_db
from common.dependencies import get_current_user_id

from .buy_service import calculate_buy_pattern
from .buy_schema import BuyPatternResponse

router = APIRouter(
    prefix="/api/insights/buy-pattern",
    tags=["insights-buy-pattern"],
)


@router.get("", response_model=BuyPatternResponse)
def get_buy_pattern(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return calculate_buy_pattern(db, user_id)