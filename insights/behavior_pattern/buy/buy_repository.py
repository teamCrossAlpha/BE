from sqlalchemy.orm import Session
from sqlalchemy import func
from trades.trades_entity import Trade


def get_buy_pattern_counts(db: Session, user_id: int):
    """
    사용자 매수 행동 유형별 건수 집계
    """
    return (
        db.query(
            Trade.behavior_type,
            func.count(Trade.id).label("count")
        )
        .filter(
            Trade.user_id == user_id,
            Trade.trade_type == "BUY",
            Trade.behavior_type.isnot(None),
        )
        .group_by(Trade.behavior_type)
        .all()
    )


def get_total_buy_count(db: Session, user_id: int):
    return (
        db.query(func.count(Trade.id))
        .filter(
            Trade.user_id == user_id,
            Trade.trade_type == "BUY",
        )
        .scalar()
    )