from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session

from trades.trades_repository import get_or_create_asset
from watchlist.watchlist_entity import Watchlist
from watchlist.watchlist_repository import (
    create_watchlist,
    delete_watchlist,
    get_by_user_ticker,
    list_by_user,
)
from watchlist.watchlist_schema import (
    WatchlistCreateRequest,
    WatchlistCreateResponse,
    WatchlistDeleteResponse,
    WatchlistItem,
    WatchlistListResponse,
)


def get_watchlist(db: Session, user_id: int) -> WatchlistListResponse:
    rows = list_by_user(db, user_id)
    return WatchlistListResponse(
        watchlistTickers=[
            WatchlistItem(ticker=r.ticker, addedAt=r.created_at) for r in rows
        ]
    )


def add_watchlist(db: Session, user_id: int, req: WatchlistCreateRequest) -> WatchlistCreateResponse:
    ticker = req.ticker.upper().strip()

    get_or_create_asset(db, ticker)

    existing = get_by_user_ticker(db, user_id, ticker)
    if existing:
        raise HTTPException(status_code=409, detail="Ticker already in watchlist")

    row = Watchlist(user_id=user_id, ticker=ticker)
    create_watchlist(db, row)

    db.commit()
    db.refresh(row)

    return WatchlistCreateResponse(status="SUCCESS", ticker=row.ticker, addedAt=row.created_at)


def remove_watchlist(db: Session, user_id: int, ticker: str) -> WatchlistDeleteResponse:
    t = ticker.upper().strip()

    row = get_by_user_ticker(db, user_id, t)
    if not row:
        raise HTTPException(status_code=404, detail="Ticker not found in watchlist")

    delete_watchlist(db, row)
    db.commit()

    return WatchlistDeleteResponse(status="DELETED", ticker=t)