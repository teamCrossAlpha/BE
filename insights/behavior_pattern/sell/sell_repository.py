from sqlalchemy.orm import Session
from sqlalchemy import func, case
from trades.trades_entity import Trade, TradeResult


def get_sell_pattern_stats(db: Session, user_id: int):

    invested_expr = case(
        (TradeResult.pnl_rate != 0,
         TradeResult.pnl_amount / TradeResult.pnl_rate),
        else_=0
    )

    return (
        db.query(
            Trade.behavior_type,
            func.count(Trade.id).label("count"),
            func.sum(
                case((TradeResult.pnl_amount > 0, 1), else_=0)
            ).label("wins"),
            func.sum(TradeResult.pnl_amount).label("total_pnl"),
            func.sum(invested_expr).label("total_invested"),
        )
        .join(TradeResult, Trade.id == TradeResult.trade_id)
        .filter(
            Trade.user_id == user_id,
            Trade.trade_type.in_(["SELL", "PARTIAL_SELL"]),
            TradeResult.pnl_status == "CLOSED",
            TradeResult.pnl_rate.isnot(None),
            Trade.behavior_type.isnot(None),
        )
        .group_by(Trade.behavior_type)
        .all()
    )