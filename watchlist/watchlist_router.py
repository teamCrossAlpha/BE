from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from common.database import get_db
from common.dependencies import get_current_user_id

from watchlist.watchlist_schema import (
    WatchlistCreateRequest,
    WatchlistCreateResponse,
    WatchlistDeleteResponse,
    WatchlistListResponse,
)
from watchlist.watchlist_service import add_watchlist, get_watchlist, remove_watchlist

router = APIRouter(prefix="/api/watchlist", tags=["watchlist"])


@router.get("", response_model=WatchlistListResponse)
def get_watchlist_api(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return get_watchlist(db, user_id)


@router.post("", response_model=WatchlistCreateResponse, status_code=201)
def add_watchlist_api(
    req: WatchlistCreateRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return add_watchlist(db, user_id, req)


@router.delete("/{ticker}", response_model=WatchlistDeleteResponse)
def remove_watchlist_api(
    ticker: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return remove_watchlist(db, user_id, ticker)