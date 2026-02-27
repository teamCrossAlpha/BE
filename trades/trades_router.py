from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from common.database import get_db
from common.dependencies import get_current_user_id
from trades.market_snapshot_schema import TradeMarketSnapshotQuantResponse
from trades.market_snapshot_service import get_trade_snapshot_quant

from trades.trades_schema import (
    TradeCreateRequest,
    TradeCreateResponse,
    TradeListResponse,
    TradeDetailResponse,
    TradeSummaryResponse,
)
from trades.trades_service import (
    create_trade_and_update_position,
    get_trade_list,
    get_trade_detail,
    get_trade_summary,
)

from trades.trade_positions_schema import TradePositionsResponse
from trades.trade_positions_service import get_trade_positions

router = APIRouter(prefix="/api/trades", tags=["Trades"])


@router.get("/summary", response_model=TradeSummaryResponse)
def read_trade_summary(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return get_trade_summary(db, user_id)


@router.get("", response_model=TradeListResponse)
def list_trades(
    sortField: str | None = Query(None),
    sortOrder: str | None = Query(None),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return get_trade_list(db, user_id, sortField, sortOrder)


@router.post("", response_model=TradeCreateResponse, status_code=201)
def create_trade(
    req: TradeCreateRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return create_trade_and_update_position(db, user_id, req)


@router.get("/positions", response_model=TradePositionsResponse)
def get_trades_by_position(
    status: str | None = Query("OPEN"),  # OPEN | CLOSED
    sort: str | None = Query("recent"),  # recent | oldest
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return get_trade_positions(db, user_id, status=status or "OPEN", sort=sort or "recent")


@router.get("/{tradeId}", response_model=TradeDetailResponse)
def read_trade_detail(
    tradeId: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return get_trade_detail(db, user_id, tradeId)


@router.get(
    "/{tradeId}/market-snapshot/quant",
    response_model=TradeMarketSnapshotQuantResponse,
)
def get_trade_market_snapshot_quant(
    tradeId: int,
    range: Literal["3M","6M","1Y"] = Query("3M"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return get_trade_snapshot_quant(db, user_id=user_id, trade_id=tradeId, rng=range)

