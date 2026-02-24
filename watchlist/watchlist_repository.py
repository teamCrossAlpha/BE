from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from watchlist.watchlist_entity import Watchlist


def get_by_user_ticker(db: Session, user_id: int, ticker: str) -> Optional[Watchlist]:
    t = ticker.upper().strip()
    return (
        db.query(Watchlist)
        .filter(Watchlist.user_id == user_id, Watchlist.ticker == t)
        .first()
    )


def list_by_user(db: Session, user_id: int) -> List[Watchlist]:
    return (
        db.query(Watchlist)
        .filter(Watchlist.user_id == user_id)
        .order_by(Watchlist.created_at.desc())
        .all()
    )


def create_watchlist(db: Session, row: Watchlist) -> Watchlist:
    db.add(row)
    db.flush()
    return row


def delete_watchlist(db: Session, row: Watchlist) -> None:
    db.delete(row)
    db.flush()