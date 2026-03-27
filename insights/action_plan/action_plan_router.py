from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from common.database import get_db
from common.dependencies import get_current_user_id

from insights.action_plan.action_plan_service import (
    get_latest_action_plan_service
)

router = APIRouter(
    prefix="/api/insights/action-plan",
    tags=["ActionPlan"]
)


@router.get("/latest")
def get_latest_action_plan(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return get_latest_action_plan_service(db, user_id)