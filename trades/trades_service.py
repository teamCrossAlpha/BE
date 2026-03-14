from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from trades.trades_entity import (
    Trade,
    TradeResult,
    BUY_BEHAVIOR_TYPES,
    SELL_BEHAVIOR_TYPES,
)
from trades.trades_schema import (
    TradeCreateRequest,
    TradeCreateResponse,
    TradeListResponse,
    TradeListItem,
    TradeDetailResponse,
    PnlPayload,
    TradeSummaryResponse,
    TradeSummaryPayload,
)
from trades.trades_repository import (
    get_or_create_asset,
    create_trade,
    create_trade_result,
    list_trades_with_results,
    get_trade_with_result,
    get_summary, close_position, get_open_position, create_position, list_position_buy_trades, get_position_state,
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


def create_trade_and_update_position(db: Session, user_id: int, req: TradeCreateRequest) -> TradeCreateResponse:
    ticker = req.ticker.upper().strip()
    _validate_behavior(req.tradeType, req.behaviorType)

    asset = get_or_create_asset(db, ticker)
    open_pos = get_open_position(db, user_id, asset.ticker)

    # BUY
    if req.tradeType == "BUY":
        if open_pos is None:
            open_pos = create_position(db, user_id, asset.ticker)
            position_action = "ENTRY"
            current_qty = 0
            current_avg = None
        else:
            current_qty, current_avg = get_position_state(db, user_id, int(open_pos.id))
            position_action = "ENTRY" if current_qty <= 0 else "ADD"

        trade = Trade(
            user_id=user_id,
            ticker=asset.ticker,
            position_id=open_pos.id,
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
        create_trade_result(db, TradeResult(trade_id=trade.id, pnl_status="OPEN"))

        db.commit()
        return TradeCreateResponse(tradeId=trade.id, status="CREATED")

    # SELL
    if open_pos is None:
        raise HTTPException(status_code=400, detail="No open position to sell")

    current_qty, current_avg = get_position_state(db, user_id, int(open_pos.id))

    if current_qty <= 0:
        raise HTTPException(status_code=400, detail="No holding to sell")

    if req.quantity > current_qty:
        raise HTTPException(status_code=400, detail="Sell quantity exceeds holding quantity")

    remaining_qty = current_qty - req.quantity
    position_action = "EXIT" if remaining_qty == 0 else "PARTIAL_EXIT"

    trade = Trade(
        user_id=user_id,
        ticker=asset.ticker,
        position_id=open_pos.id,
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

    pnl_amount = None
    pnl_rate = None
    if current_avg is not None and current_avg != 0:
        pnl_amount = (req.price - current_avg) * Decimal(req.quantity)
        pnl_rate = (req.price - current_avg) / current_avg

    if position_action == "EXIT":
        close_position(db, open_pos)
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
    return TradeCreateResponse(tradeId=trade.id, status="CREATED")

def get_trade_list(db: Session, user_id: int, sort_field: str | None, sort_order: str | None) -> TradeListResponse:
    rows = list_trades_with_results(db, user_id, sort_field, sort_order)

    items: list[TradeListItem] = []

    for trade, result in rows:
        pnl_payload = None

        # SELL일 때만 pnl 객체 생성, BUY일 때는 null
        if trade.trade_type == "SELL":
            if result.pnl_rate is not None and result.pnl_amount is not None:
                pnl_payload = PnlPayload(
                    profitRate=float(result.pnl_rate),
                    profitAmount=float(result.pnl_amount),
                )

        items.append(
            TradeListItem(
                tradeId=trade.id,
                tradeDate=trade.trade_date,
                ticker=trade.ticker,
                tradeType=trade.trade_type,
                price=float(trade.price),
                quantity=int(trade.quantity),
                pnlStatus=result.pnl_status,
                pnl=pnl_payload,
                confidence=int(trade.confidence) if trade.confidence is not None else None,
                behaviorType=trade.behavior_type,
                memo=trade.memo,
                positionAction=trade.position_action,
            )
        )

    return TradeListResponse(trades=items)


def get_trade_detail(db: Session, user_id: int, trade_id: int) -> TradeDetailResponse:
    row = get_trade_with_result(db, user_id, trade_id)
    if not row:
        raise HTTPException(status_code=404, detail="Trade not found")

    trade, result = row

    buy_trades = list_position_buy_trades(db, user_id, int(trade.position_id))

    buy_qty = 0
    buy_cost = Decimal("0")
    for bt in buy_trades:
        q = int(bt.quantity)
        buy_qty += q
        buy_cost += Decimal(str(bt.price)) * Decimal(q)

    avg_price: float | None = None
    if buy_qty > 0:
        avg_price = float(buy_cost / Decimal(buy_qty))

    pnl_payload = None
    if trade.trade_type == "SELL":
        if result.pnl_rate is not None and result.pnl_amount is not None:
            pnl_payload = PnlPayload(
                profitRate=float(result.pnl_rate),
                profitAmount=float(result.pnl_amount),
            )

    return TradeDetailResponse(
        tradeId=trade.id,
        ticker=trade.ticker,
        tradeType=trade.trade_type,
        tradeDate=trade.trade_date,
        price=float(trade.price),
        quantity=int(trade.quantity),
        confidence=int(trade.confidence) if trade.confidence is not None else None,
        behaviorType=trade.behavior_type,
        memo=trade.memo,
        pnlStatus=result.pnl_status,
        pnl=pnl_payload,
        averagePrice=avg_price,
    )


def get_trade_summary(db: Session, user_id: int) -> TradeSummaryResponse:
    total_trades, win_rate, avg_conf, best_return = get_summary(db, user_id)
    return TradeSummaryResponse(
        summary=TradeSummaryPayload(
            totalTrades=int(total_trades),
            winRate=float(win_rate),
            averageConfidence=int(avg_conf),
            bestTradeReturn=float(best_return),
        )
    )