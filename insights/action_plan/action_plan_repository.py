from sqlalchemy.orm import Session
from insights.action_plan.action_plan_entity import ActionPlan


def get_latest_action_plan(db: Session, user_id: int):
    return (
        db.query(ActionPlan)
        .filter(ActionPlan.user_id == user_id)
        .order_by(ActionPlan.created_at.desc())
        .first()
    )


def create_action_plan(db: Session, action_plan: ActionPlan):
    db.add(action_plan)
    db.commit()
    db.refresh(action_plan)
    return action_plan