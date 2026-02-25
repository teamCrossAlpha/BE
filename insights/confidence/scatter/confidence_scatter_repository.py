from sqlalchemy.orm import Session
from trades.trades_entity import Trade, TradeResult


def get_completed_sell_trades_with_confidence(db: Session, user_id: int):
    return (
        db.query(
            Trade.ticker,
            Trade.confidence,
            Trade.trade_date,
            TradeResult.pnl_rate,
        )
        .join(TradeResult, Trade.id == TradeResult.trade_id)
        .filter(
            Trade.user_id == user_id,
            Trade.trade_type.in_(["SELL", "PARTIAL_SELL"]),
            TradeResult.pnl_rate.isnot(None),
            Trade.confidence.isnot(None),
        )
        .all()
    )