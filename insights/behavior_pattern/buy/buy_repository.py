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


def find_buy_for_sell(db: Session, sell_trade):
    return (
        db.query(Trade)
        .filter(
            Trade.user_id == sell_trade.user_id,
            Trade.ticker == sell_trade.ticker,
            Trade.trade_type == "BUY",
            Trade.trade_date < sell_trade.trade_date,
        )
        .order_by(Trade.trade_date.desc())
        .first()
    )