from sqlalchemy.orm import Session
from sqlalchemy import case, func
from trades.trades_entity import Trade, TradeResult


def get_confidence_range_stats(db: Session, user_id: int):

    invested_expr = case(
        (TradeResult.pnl_rate != 0,
         TradeResult.pnl_amount / TradeResult.pnl_rate),
        else_=0
    )

    confidence_range = case(
        (Trade.confidence >= 80, "80+"),
        (Trade.confidence >= 60, "60~79"),
        (Trade.confidence >= 40, "40~59"),
        (Trade.confidence >= 20, "20~39"),
        else_="0~19",
    )

    return (
        db.query(
            confidence_range.label("range_label"),
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
            Trade.confidence.isnot(None),
        )
        .group_by(confidence_range)
        .all()
    )