from sqlalchemy.orm import Session
from .confidence_scatter_repository import get_completed_sell_trades_with_confidence
from .confidence_scatter_schema import (
    ConfidenceScatterResponse,
    CompletedTrade,
    SellTradeInfo,
)


def calculate_confidence_scatter(db: Session, user_id: int):
    rows = get_completed_sell_trades_with_confidence(db, user_id)

    trades = []

    for row in rows:
        trades.append(
            CompletedTrade(
                ticker=row.ticker,
                confidence=row.confidence,
                pnlPercent=round(row.pnl_rate * 100, 2),
                sellTrade=SellTradeInfo(
                    date=row.trade_date.isoformat(),
                ),
            )
        )

    return ConfidenceScatterResponse(
        totalCompletedTrades=len(trades),
        trades=trades,
    )