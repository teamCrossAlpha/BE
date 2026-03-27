from pydantic import BaseModel
from typing import List


class ActionPlanItem(BaseModel):
    title: str
    summary: str
    referenced_trade_ids: List[int]


class ActionPlanResponse(BaseModel):
    buy_action_plan: ActionPlanItem
    sell_action_plan: ActionPlanItem
    created_at: str


class ActionPlanCreateResponse(BaseModel):
    generated: bool
    message: str
    action_plan_id: int | None = None