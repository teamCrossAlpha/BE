from typing import Literal

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from common.database import get_db
from common.dependencies import get_current_user_id

from trades.trades_schema import TradeCreateRequest
from trades.trades_service import (
    create_trade_and_update_position,
    get_trade_list,
    get_trade_detail,
    get_trade_summary,
)
from trades.market_snapshot_service import (
    get_trade_snapshot_quant,
)
from trades.market_snapshot_schema import (
    TradeMarketSnapshotQuantResponse,
)

router = APIRouter(prefix="/api/trades", tags=["trades"])


def _pnl_obj(trade):
    """
    - pnl_rate/pnl_amount 값이 '둘 다' 없으면 pnl: null
    - 하나라도 있으면 pnl 객체로 내려줌
    """
    if not getattr(trade, "result", None):
        return None

    rate = trade.result.pnl_rate
    amt = trade.result.pnl_amount

    if rate is None and amt is None:
        return None

    return {
        "profitRate": float(rate) if rate is not None else None,
        "profitAmount": float(amt) if amt is not None else None,
    }


def _pnl_status(trade) -> str:
    if not getattr(trade, "result", None):
        return "OPEN"
    return trade.result.pnl_status


@router.post("", status_code=status.HTTP_201_CREATED)
def create_trade_api(
    req: TradeCreateRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    trade_id = create_trade_and_update_position(db, user_id, req)
    return {"tradeId": trade_id, "status": "CREATED"}


@router.get("")
def list_trades_api(
    sortField: str | None = Query(default=None),
    sortOrder: str | None = Query(default="desc"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    trades = get_trade_list(db, user_id, sortField, sortOrder)

    return {
        "trades": [
            {
                "tradeId": t.id,
                "tradeDate": t.trade_date,
                "ticker": t.ticker,
                "tradeType": t.trade_type,
                "price": float(t.price),
                "quantity": t.quantity,
                "pnl": _pnl_obj(t),
                "pnlStatus": _pnl_status(t),
                "confidence": t.confidence,
                "behaviorType": t.behavior_type,
                "memo": t.memo,
            }
            for t in trades
        ]
    }

@router.get("/summary")
def trades_summary_api(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    total_trades, win_rate, avg_conf, best_return = get_trade_summary(db, user_id)
    return {
        "summary": {
            "totalTrades": total_trades,
            "winRate": win_rate,
            "averageConfidence": avg_conf,
            "bestTradeReturn": best_return,
        }
    }

@router.get("/{tradeId}")
def get_trade_detail_api(
    tradeId: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    t = get_trade_detail(db, user_id, tradeId)
    if not t:
        raise HTTPException(status_code=404, detail="Trade not found")

    return {
        "tradeId": t.id,
        "ticker": t.ticker,
        "tradeType": t.trade_type,
        "tradeDate": t.trade_date,
        "price": float(t.price),
        "quantity": t.quantity,
        "confidence": t.confidence,
        "behaviorType": t.behavior_type,
        "memo": t.memo,
        "pnl": _pnl_obj(t),
        "pnlStatus": _pnl_status(t),
    }


@router.get(
    "/api/trades/{trade_id}/market-snapshot/quant",
    response_model=TradeMarketSnapshotQuantResponse,
)
def get_trade_market_snapshot_quant(
    trade_id: int,
    range: Literal["3M","6M","1Y"] = Query("3M"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return get_trade_snapshot_quant(db, user_id=user_id, trade_id=trade_id, rng=range)  # type: ignore[arg-type]

