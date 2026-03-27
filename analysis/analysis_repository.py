from __future__ import annotations

from datetime import date
from typing import List, Tuple

from sqlalchemy.orm import Session

from portfolio.portfolio_repository import list_holdings_by_user
from trades.trades_entity import Asset, Trade, TradeResult


def list_sell_trades_with_results(
    db: Session,
    user_id: int,
    start_date: date | None = None,
) -> List[Tuple[Trade, TradeResult]]:
    q = (
        db.query(Trade, TradeResult)
        .join(TradeResult, TradeResult.trade_id == Trade.id)
        .filter(
            Trade.user_id == user_id,
            Trade.trade_type == "SELL",
            TradeResult.pnl_amount.isnot(None),
        )
        .order_by(Trade.trade_date.asc(), Trade.id.asc())
    )

    if start_date is not None:
        q = q.filter(Trade.trade_date >= start_date)

    return q.all()


def list_sell_trades_with_results_and_rate(
    db: Session,
    user_id: int,
    start_date: date | None = None,
) -> List[Tuple[Trade, TradeResult]]:
    q = (
        db.query(Trade, TradeResult)
        .join(TradeResult, TradeResult.trade_id == Trade.id)
        .filter(
            Trade.user_id == user_id,
            Trade.trade_type == "SELL",
            TradeResult.pnl_amount.isnot(None),
            TradeResult.pnl_rate.isnot(None),
        )
        .order_by(Trade.trade_date.asc(), Trade.id.asc())
    )

    if start_date is not None:
        q = q.filter(Trade.trade_date >= start_date)

    return q.all()


def list_user_holdings(db: Session, user_id: int):
    return list_holdings_by_user(db, user_id)


def get_asset_by_ticker(db: Session, ticker: str) -> Asset | None:
    return db.query(Asset).filter(Asset.ticker == ticker).first()