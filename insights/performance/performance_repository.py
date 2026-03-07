from sqlalchemy.orm import Session
from trades.trades_entity import Trade, TradeResult


def get_sell_trades_for_performance(db: Session, user_id: int):
    """
    SELL 거래 중 pnl_rate가 존재하는 모든 매도건
    (부분매도 포함)
    오래된 순 정렬
    """
    return (
        db.query(Trade)
        .join(TradeResult, Trade.id == TradeResult.trade_id)
        .filter(
            Trade.user_id == user_id,
            Trade.trade_type == "SELL",
            TradeResult.pnl_rate.isnot(None),  # pnl 있는 매도만
        )
        .order_by(Trade.trade_date.asc())
        .all()
    )