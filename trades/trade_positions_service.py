from __future__ import annotations

from decimal import Decimal
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from marketdata.marketdata_service import get_cached_quote_fields
from trades.trades_entity import Holding, TradePosition, Trade
from trades.trade_positions_repository import list_positions
from trades.trade_positions_schema import (
    TradePositionsResponse,
    OpenPositionItem,
    ClosedPositionItem,
    PositionTradeItem,
    PnlPayload,
)


def _dec(v) -> Optional[Decimal]:
    if v is None:
        return None
    return Decimal(str(v))


def _make_trade_item(t: Trade) -> PositionTradeItem:
    pnl = None
    # SELL이면 TradeResult에 pnl이 들어있을 수 있음
    if t.trade_type == "SELL" and t.result is not None:
        if t.result.pnl_rate is not None and t.result.pnl_amount is not None:
            pnl = PnlPayload(
                profitRate=float(t.result.pnl_rate),
                profitAmount=float(t.result.pnl_amount),
            )

    return PositionTradeItem(
        tradeId=int(t.id),
        tradeDate=t.trade_date,
        tradeType=t.trade_type,
        positionAction=t.position_action,
        price=float(t.price),
        quantity=int(t.quantity),
        pnl=pnl,
    )


def _get_holding(db: Session, user_id: int, ticker: str) -> Optional[Holding]:
    return (
        db.query(Holding)
        .filter(Holding.user_id == user_id, Holding.ticker == ticker.upper().strip())
        .first()
    )


def _calc_unrealized_pnl(
    current_price: Decimal,
    holding_qty: int,
    avg_price: Optional[Decimal],
) -> Optional[PnlPayload]:
    if avg_price is None:
        return None
    qty = Decimal(int(holding_qty))
    if qty <= 0:
        return None

    cost = avg_price * qty
    if cost == 0:
        return None

    profit_amount = (current_price - avg_price) * qty
    profit_rate = profit_amount / cost

    return PnlPayload(
        profitRate=float(profit_rate),
        profitAmount=float(profit_amount),
    )


def _calc_closed_position_summary(position: TradePosition) -> tuple[int, Optional[Decimal], Optional[PnlPayload]]:
    """
    CLOSED 포지션 요약:
      - totalBuyQuantity(총 매입 수량)
      - averagePrice(가중평균 매입단가)
      - pnl(실현손익): 해당 포지션에 속한 SELL trade들의 pnl_amount 합산
    """
    buy_qty = 0
    buy_cost = Decimal("0")

    realized_profit_amount = Decimal("0")
    has_realized = False

    for t in position.trades:
        if t.trade_type == "BUY":
            q = int(t.quantity)
            buy_qty += q
            buy_cost += Decimal(str(t.price)) * Decimal(q)

        if t.trade_type == "SELL" and t.result is not None:
            if t.result.pnl_amount is not None:
                realized_profit_amount += Decimal(str(t.result.pnl_amount))
                has_realized = True

    avg_price = None
    if buy_qty > 0:
        avg_price = buy_cost / Decimal(buy_qty)

    pnl = None
    if has_realized and avg_price is not None and buy_qty > 0:
        cost_basis = avg_price * Decimal(buy_qty)
        if cost_basis != 0:
            pnl = PnlPayload(
                profitRate=float(realized_profit_amount / cost_basis),
                profitAmount=float(realized_profit_amount),
            )

    return buy_qty, avg_price, pnl


def get_trade_positions(
    db: Session,
    user_id: int,
    status: str,
    sort: str = "recent",
) -> TradePositionsResponse:
    status = (status or "").upper().strip()
    if status not in ("OPEN", "CLOSED"):
        raise HTTPException(status_code=400, detail="Unsupported status (OPEN|CLOSED)")

    sort = (sort or "recent").lower().strip()
    if sort not in ("recent", "oldest"):
        raise HTTPException(status_code=400, detail="Unsupported sort (recent|oldest)")

    positions = list_positions(db, user_id, status=status, sort=sort)

    if status == "OPEN":
        open_items: list[OpenPositionItem] = []

        for p in positions:
            ticker = p.ticker.upper().strip()

            holding = _get_holding(db, user_id, ticker)
            holding_qty = int(holding.quantity) if holding else 0
            avg_price = _dec(holding.average_price) if (holding and holding.average_price is not None) else None

            # 현재가(캐시)
            q = get_cached_quote_fields(db, ticker, ttl_seconds=180)
            current_price = Decimal(str(q.price))

            pnl = _calc_unrealized_pnl(
                current_price=current_price,
                holding_qty=holding_qty,
                avg_price=avg_price,
            )

            trades_sorted = sorted(p.trades, key=lambda x: (x.trade_date, x.id))
            trade_items = [_make_trade_item(t) for t in trades_sorted]

            open_items.append(
                OpenPositionItem(
                    positionId=int(p.id),
                    ticker=ticker,
                    holdingQuantity=holding_qty,
                    averagePrice=float(avg_price) if avg_price is not None else None,
                    totalTrades=len(trade_items),
                    pnl=pnl,
                    openedAt=p.opened_at,
                    trades=trade_items,
                )
            )

        return TradePositionsResponse(
            status="OPEN",
            openPositions=open_items,
            closedPositions=[],
        )

    # CLOSED
    closed_items: list[ClosedPositionItem] = []

    for p in positions:
        ticker = p.ticker.upper().strip()

        buy_qty, avg_price, pnl = _calc_closed_position_summary(p)

        trades_sorted = sorted(p.trades, key=lambda x: (x.trade_date, x.id))
        trade_items = [_make_trade_item(t) for t in trades_sorted]

        closed_items.append(
            ClosedPositionItem(
                positionId=int(p.id),
                ticker=ticker,
                totalBuyQuantity=int(buy_qty),
                averagePrice=float(avg_price) if avg_price is not None else None,
                totalTrades=len(trade_items),
                pnl=pnl,
                openedAt=p.opened_at,
                closedAt=p.closed_at,
                trades=trade_items,
            )
        )

    return TradePositionsResponse(
        status="CLOSED",
        openPositions=[],
        closedPositions=closed_items,
    )