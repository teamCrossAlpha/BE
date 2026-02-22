from decimal import Decimal
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from trades.trades_entity import (
    Trade,
    TradeResult,
    BUY_BEHAVIOR_TYPES,
    SELL_BEHAVIOR_TYPES,
)
from trades.trades_schema import TradeCreateRequest
from trades.trades_repository import (
    get_or_create_asset,
    get_holding,
    upsert_holding,
    create_trade,
    create_trade_result,
    list_trades,
    get_trade,
    get_summary,
)


def _validate_behavior(trade_type: str, behavior_type: str):
    if trade_type == "BUY":
        if behavior_type not in BUY_BEHAVIOR_TYPES:
            raise HTTPException(status_code=400, detail="Invalid behaviorType for BUY")
    elif trade_type == "SELL":
        if behavior_type not in SELL_BEHAVIOR_TYPES:
            raise HTTPException(status_code=400, detail="Invalid behaviorType for SELL")
    else:
        raise HTTPException(status_code=400, detail="Invalid tradeType")


def create_trade_and_update_position(db: Session, user_id: int, req: TradeCreateRequest) -> int:
    ticker = req.ticker.upper().strip()
    _validate_behavior(req.tradeType, req.behaviorType)

    asset = get_or_create_asset(db, ticker)

    holding = get_holding(db, user_id, asset.ticker)
    prev_qty = holding.quantity if holding else 0
    prev_avg = Decimal(holding.average_price) if (holding and holding.average_price is not None) else None

    # BUY
    if req.tradeType == "BUY":
        if prev_qty <= 0:
            position_action = "ENTRY"
            new_qty = req.quantity
            new_avg = req.price
        else:
            position_action = "ADD"
            new_qty = prev_qty + req.quantity
            if prev_avg is None:
                prev_avg = Decimal(req.price)
            new_avg = (prev_avg * Decimal(prev_qty) + req.price * Decimal(req.quantity)) / Decimal(new_qty)

        upsert_holding(db, user_id, asset.ticker, new_qty, new_avg)

        trade = Trade(
            user_id=user_id,
            ticker=asset.ticker,
            trade_type="BUY",
            trade_date=req.tradeDate,
            price=req.price,
            quantity=req.quantity,
            confidence=req.confidence,
            behavior_type=req.behaviorType,
            memo=req.memo,
            position_action=position_action,
        )
        create_trade(db, trade)

        # BUY는 결과 OPEN
        create_trade_result(db, TradeResult(trade_id=trade.id, pnl_status="OPEN"))

        db.commit()
        return trade.id

    # SELL
    if prev_qty <= 0:
        raise HTTPException(status_code=400, detail="No holding to sell")

    if req.quantity > prev_qty:
        raise HTTPException(status_code=400, detail="Sell quantity exceeds holding quantity")

    remaining_qty = prev_qty - req.quantity
    position_action = "EXIT" if remaining_qty == 0 else "PARTIAL_EXIT"

    # avg는 유지
    upsert_holding(db, user_id, asset.ticker, remaining_qty, prev_avg)

    trade = Trade(
        user_id=user_id,
        ticker=asset.ticker,
        trade_type="SELL",
        trade_date=req.tradeDate,
        price=req.price,
        quantity=req.quantity,
        confidence=req.confidence,
        behavior_type=req.behaviorType,
        memo=req.memo,
        position_action=position_action,
    )
    create_trade(db, trade)

    # pnl 계산(평단 기준)
    pnl_amount = None
    pnl_rate = None
    if prev_avg is not None and prev_avg != 0:
        pnl_amount = (req.price - prev_avg) * Decimal(req.quantity)
        pnl_rate = (req.price - prev_avg) / prev_avg

    if position_action == "EXIT":
        create_trade_result(
            db,
            TradeResult(
                trade_id=trade.id,
                pnl_status="CLOSED",
                pnl_amount=pnl_amount,
                pnl_rate=pnl_rate,
                closed_at=datetime.utcnow(),
            ),
        )
    else:
        create_trade_result(
            db,
            TradeResult(
                trade_id=trade.id,
                pnl_status="OPEN",
                pnl_amount=pnl_amount,
                pnl_rate=pnl_rate,
            ),
        )

    db.commit()
    return trade.id


def get_trade_list(db: Session, user_id: int, sort_field: str | None, sort_order: str | None):
    return list_trades(db, user_id, sort_field, sort_order)


def get_trade_detail(db: Session, user_id: int, trade_id: int):
    return get_trade(db, user_id, trade_id)


def get_trade_summary(db: Session, user_id: int):
    return get_summary(db, user_id)
