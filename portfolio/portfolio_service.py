from __future__ import annotations

from decimal import Decimal
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import date, timedelta

from marketdata.marketdata_service import get_cached_quote_fields
from portfolio.portfolio_repository import (
    list_holdings_by_user,
    get_holding_by_user_ticker,
    create_holding,
    delete_holding,
    list_snapshots_range,
)
from portfolio.portfolio_schema import (
    HoldingsListResponse,
    HoldingItem,
    HoldingUpsertRequest,
    HoldingUpdateRequest,
    HoldingUpsertResponse,
    HoldingDeleteResponse,
    PortfolioSummaryResponse,
    PortfolioPerformancePoint,
    PortfolioPerformanceResponse,
)
from trades.trades_entity import Holding
from trades.trades_repository import get_or_create_asset


RANGE_TO_DAYS: Dict[str, int] = {
    "30D": 30,
}


def _to_float(v: Optional[Decimal]) -> Optional[float]:
    if v is None:
        return None
    return float(v)


def get_holdings_list(db: Session, user_id: int) -> HoldingsListResponse:
    rows = list_holdings_by_user(db, user_id)

    items: list[HoldingItem] = []
    for h in rows:
        t = (h.ticker or "").upper().strip()

        # 1) 현재가 캐시 조회 (없거나 stale이면 yfinance로 갱신)
        price_row = get_cached_quote_fields(db, t, ttl_seconds=180)

        current_price = _to_float(price_row.price)

        avg_price = _to_float(h.average_price)

        # 2) 수익률 = (현재가 - 평균매입가) / 평균매입가
        profit_rate: Optional[float] = None
        if avg_price is not None and avg_price != 0 and current_price is not None:
            profit_rate = (current_price - avg_price) / avg_price

        items.append(
            HoldingItem(
                ticker=t,
                quantity=int(h.quantity),
                averagePrice=avg_price,
                currentPrice=current_price,
                profitRate=profit_rate,
            )
        )

    return HoldingsListResponse(holdings=items)


def create_portfolio_holding(db: Session, user_id: int, req: HoldingUpsertRequest) -> HoldingUpsertResponse:
    ticker = req.ticker.upper().strip()

    # assets FK 때문에 assets row 보장
    get_or_create_asset(db, ticker)

    existing = get_holding_by_user_ticker(db, user_id, ticker)
    if existing:
        raise HTTPException(status_code=409, detail="Holding already exists")

    h = Holding(
        user_id=user_id,
        ticker=ticker,
        quantity=req.quantity,
        average_price=req.averagePrice,
    )
    create_holding(db, h)
    db.commit()
    db.refresh(h)

    return HoldingUpsertResponse(
        status="SUCCESS",
        ticker=h.ticker,
        quantity=h.quantity,
        averagePrice=h.average_price,
        createdAt=h.created_at,
    )


def update_portfolio_holding(db: Session, user_id: int, ticker: str, req: HoldingUpdateRequest) -> HoldingUpsertResponse:
    t = ticker.upper().strip()
    get_or_create_asset(db, t)

    h = get_holding_by_user_ticker(db, user_id, t)

    if req.action == "ADD":
        # ADD일 때는 price 필수
        if req.price is None:
            raise HTTPException(status_code=400, detail="price is required for ADD")

        add_qty = int(req.quantity)
        add_price = Decimal(req.price)

        if h is None:
            # 신규 생성
            h = Holding(
                user_id=user_id,
                ticker=t,
                quantity=add_qty,
                average_price=add_price,
            )
            create_holding(db, h)
        else:
            prev_qty = int(h.quantity)
            prev_avg = Decimal(h.average_price) if h.average_price is not None else None

            new_qty = prev_qty + add_qty

            # 평단 가중평균: (prev_avg*prev_qty + add_price*add_qty) / new_qty
            if prev_avg is None:
                new_avg = add_price
            else:
                new_avg = (prev_avg * Decimal(prev_qty) + add_price * Decimal(add_qty)) / Decimal(new_qty)

            h.quantity = new_qty
            h.average_price = new_avg

        db.commit()
        db.refresh(h)

        return HoldingUpsertResponse(
            status="SUCCESS",
            ticker=h.ticker,
            quantity=h.quantity,
            averagePrice=h.average_price,
            updatedAt=h.updated_at,
        )

    if req.action == "REDUCE":
        if h is None:
            raise HTTPException(status_code=404, detail="Holding not found")

        reduce_qty = int(req.quantity)
        prev_qty = int(h.quantity)

        if reduce_qty > prev_qty:
            raise HTTPException(status_code=400, detail="Reduce quantity exceeds holding quantity")

        new_qty = prev_qty - reduce_qty

        if new_qty == 0:
            # 0이면 삭제
            delete_holding(db, h)
            db.commit()
            return HoldingUpsertResponse(
                status="SUCCESS",
                ticker=t,
                quantity=0,
                averagePrice=None,
                updatedAt=None,
            )

        # 평단은 유지
        h.quantity = new_qty
        db.commit()
        db.refresh(h)

        return HoldingUpsertResponse(
            status="SUCCESS",
            ticker=h.ticker,
            quantity=h.quantity,
            averagePrice=h.average_price,
            updatedAt=h.updated_at,
        )

    # 방어
    raise HTTPException(status_code=400, detail="Invalid action")


def delete_portfolio_holding(db: Session, user_id: int, ticker: str) -> HoldingDeleteResponse:
    t = ticker.upper().strip()

    h = get_holding_by_user_ticker(db, user_id, t)
    if not h:
        raise HTTPException(status_code=404, detail="Holding not found")

    delete_holding(db, h)
    db.commit()

    return HoldingDeleteResponse(status="DELETED", ticker=t)


def get_portfolio_summary(db: Session, user_id: int) -> PortfolioSummaryResponse:
    holdings = list_holdings_by_user(db, user_id)

    total_value = Decimal("0")  # 현재 전체 평가금액
    total_profit_amount = Decimal("0")  # 총 수익금
    total_cost_basis = Decimal("0") # 총 매인원가

    for h in holdings:
        ticker = h.ticker.upper().strip()

        # 현재가: 캐시(없거나 stale이면 yfinance 갱신)
        q = get_cached_quote_fields(db, ticker, ttl_seconds=180)
        current_price = Decimal(q.price)

        qty = Decimal(int(h.quantity))
        total_value += current_price * qty

        if h.average_price is not None:
            avg = Decimal(h.average_price)
            total_cost_basis += avg * qty
            total_profit_amount += (current_price - avg) * qty

    if total_cost_basis > 0:
        total_profit_rate = total_profit_amount / total_cost_basis
        return PortfolioSummaryResponse(
            totalValue=float(total_value),
            totalProfitRate=float(total_profit_rate),
            totalProfitAmount=float(total_profit_amount),
        )

    # avg가 없는 종목만 있는 경우
    return PortfolioSummaryResponse(
        totalValue=float(total_value),
        totalProfitRate=None,
        totalProfitAmount=None,
    )


def _resolve_range_days(rng: str) -> int:
    rng = (rng or "30D").upper().strip()
    if rng not in RANGE_TO_DAYS:
        raise HTTPException(status_code=400, detail="Unsupported range")
    return RANGE_TO_DAYS[rng]


def _build_date_series(end_inclusive: date, days: int) -> List[date]:
    """
    days=30 이면:
    end_inclusive 포함해서 총 30개 날짜 생성
    (end - 29) ~ end
    """
    start = end_inclusive - timedelta(days=days - 1)
    return [start + timedelta(days=i) for i in range(days)]


def get_portfolio_performance(db: Session, user_id: int, rng: str = "30D") -> PortfolioPerformanceResponse:
    days = _resolve_range_days(rng)

    # 오늘 포함
    today = date.today()
    dates = _build_date_series(today, days)

    from_date = dates[0]
    to_date = dates[-1]

    rows = list_snapshots_range(db, user_id, from_date, to_date)

    # date -> total_value 맵
    value_map: Dict[date, float] = {r.captured_date: float(r.total_value) for r in rows}

    # forward-fill: 이전 값이 없으면 None으로 두었다가, 나중에 첫 값도 없으면 0으로
    series: List[PortfolioPerformancePoint] = []
    last_value: float | None = None

    for d in dates:
        v = value_map.get(d)
        if v is None:
            if last_value is None:
                # 아직 이전 값이 없는 구간 -> 일단 None
                series.append(PortfolioPerformancePoint(date=d, value=0.0))  # 임시 0
            else:
                series.append(PortfolioPerformancePoint(date=d, value=last_value))
        else:
            last_value = v
            series.append(PortfolioPerformancePoint(date=d, value=v))

    return PortfolioPerformanceResponse(range=rng, series=series)