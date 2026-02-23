from sqlalchemy.orm import Session
from trades.trades_entity import Trade, TradeResult


def get_completed_sell_trades(db: Session, user_id: int):
    return (
        db.query(Trade)
        .join(TradeResult, Trade.id == TradeResult.trade_id)
        .filter(
            Trade.user_id == user_id,
            Trade.trade_type == "SELL",
            TradeResult.pnl_rate.isnot(None),
        )
        .all()
    )