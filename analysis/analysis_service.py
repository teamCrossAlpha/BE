from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta, datetime
from decimal import Decimal
from typing import Dict, List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from analysis.analysis_repository import (
    get_asset_by_ticker,
    list_sell_trades_with_results,
    list_sell_trades_with_results_and_rate,
    list_user_holdings,
)
from analysis.analysis_schema import (
    AnalysisRangeMonthly,
    AnalysisRangeCumulative,
    MonthlyPerformanceItem,
    MonthlyPerformanceResponse,
    CumulativeProfitPoint,
    CumulativeProfitResponse,
    SectorAllocationItem,
    SectorAllocationResponse,
)
from marketdata.marketdata_service import get_cached_quote_fields


def _today() -> date:
    return date.today()


def _resolve_monthly_start(rng: str) -> date | None:
    today = _today()
    rng = (rng or "6M").upper().strip()

    if rng == "6M":
        return today - timedelta(days=31 * 6)
    if rng == "1Y":
        return today - timedelta(days=366)
    if rng == "ALL":
        return None

    raise HTTPException(status_code=400, detail="Unsupported range")


def _resolve_cumulative_start(rng: str) -> date | None:
    today = _today()
    rng = (rng or "3M").upper().strip()

    if rng == "1M":
        return today - timedelta(days=31)
    if rng == "3M":
        return today - timedelta(days=93)
    if rng == "6M":
        return today - timedelta(days=186)
    if rng == "1Y":
        return today - timedelta(days=366)
    if rng == "YTD":
        return date(today.year, 1, 1)
    if rng == "ALL":
        return None

    raise HTTPException(status_code=400, detail="Unsupported range")


def _month_key(d: date) -> str:
    return d.strftime("%Y-%m")


def _safe_decimal(v) -> Decimal:
    if v is None:
        return Decimal("0")
    return Decimal(str(v))


def _get_group_key(d: date, rng: str) -> str:
    rng = (rng or "").upper().strip()

    if rng in ("1M", "3M"):
        return d.strftime("%Y-%m-%d")  # day

    # 6M / 1Y / YTD / ALL
    return d.strftime("%Y-%m")  # month


def _sort_group_key(key: str, rng: str) -> datetime:
    rng = (rng or "").upper().strip()

    if rng in ("1M", "3M"):
        return datetime.strptime(key, "%Y-%m-%d")

    return datetime.strptime(key, "%Y-%m")


def get_monthly_performance(
    db: Session,
    user_id: int,
    rng: AnalysisRangeMonthly = "6M",
) -> MonthlyPerformanceResponse:
    start_date = _resolve_monthly_start(rng)
    rows = list_sell_trades_with_results_and_rate(db, user_id, start_date)

    monthly_amount_sum: Dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    monthly_cost_sum: Dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    monthly_trade_count: Dict[str, int] = defaultdict(int)

    total_trades = 0

    for trade, result in rows:
        ym = _month_key(trade.trade_date)
        pnl_amount = _safe_decimal(result.pnl_amount)
        pnl_rate = _safe_decimal(result.pnl_rate)

        cost_basis = Decimal("0")
        if pnl_rate != 0:
            cost_basis = pnl_amount / pnl_rate

        monthly_amount_sum[ym] += pnl_amount
        monthly_cost_sum[ym] += cost_basis
        monthly_trade_count[ym] += 1
        total_trades += 1

    items: List[MonthlyPerformanceItem] = []
    for ym in sorted(monthly_trade_count.keys()):
        cost_sum = monthly_cost_sum[ym]
        return_rate = float(monthly_amount_sum[ym] / cost_sum) if cost_sum != 0 else 0.0

        items.append(
            MonthlyPerformanceItem(
                yearMonth=ym,
                returnRate=return_rate,
                tradeCount=monthly_trade_count[ym],
            )
        )

    return MonthlyPerformanceResponse(
        range=rng,
        totalTrades=total_trades,
        monthlyPerformance=items,
    )


def get_cumulative_profit(
    db: Session,
    user_id: int,
    rng: AnalysisRangeCumulative = "3M",
) -> CumulativeProfitResponse:
    start_date = _resolve_cumulative_start(rng)
    rows = list_sell_trades_with_results(db, user_id, start_date)

    grouped_pnl: Dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    total_trades = 0

    for trade, result in rows:
        key = _get_group_key(trade.trade_date, rng)
        grouped_pnl[key] += _safe_decimal(result.pnl_amount)
        total_trades += 1

    cumulative = Decimal("0")
    series: List[CumulativeProfitPoint] = []

    for key in sorted(grouped_pnl.keys(), key=lambda k: _sort_group_key(k, rng)):
        cumulative += grouped_pnl[key]
        series.append(
            CumulativeProfitPoint(
                date=key,
                profit=float(cumulative),
            )
        )

    if not series:
        return CumulativeProfitResponse(
            range=rng,
            totalTrades=0,
            finalProfit=0.0,
            maxProfit=0.0,
            minProfit=0.0,
            series=[],
        )

    profits = [p.profit for p in series]

    return CumulativeProfitResponse(
        range=rng,
        totalTrades=total_trades,
        finalProfit=profits[-1],
        maxProfit=max(profits),
        minProfit=min(profits),
        series=series,
    )


def get_sector_allocation(
    db: Session,
    user_id: int,
) -> SectorAllocationResponse:
    holdings = list_user_holdings(db, user_id)

    sector_value_sum: Dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    sector_profit_amount_sum: Dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    sector_cost_sum: Dict[str, Decimal] = defaultdict(lambda: Decimal("0"))

    total_value = Decimal("0")

    for h in holdings:
        ticker = (h.ticker or "").upper().strip()
        if not ticker:
            continue

        asset = get_asset_by_ticker(db, ticker)
        sector = getattr(asset, "sector", None) or "Unknown"

        quote = get_cached_quote_fields(db, ticker, ttl_seconds=180)
        current_price = _safe_decimal(quote.price)
        qty = Decimal(int(h.quantity))

        value = current_price * qty
        total_value += value
        sector_value_sum[sector] += value

        if h.average_price is not None:
            avg = _safe_decimal(h.average_price)
            cost = avg * qty
            profit_amount = (current_price - avg) * qty

            sector_cost_sum[sector] += cost
            sector_profit_amount_sum[sector] += profit_amount

    items: List[SectorAllocationItem] = []

    for sector, value in sector_value_sum.items():
        weight = float(value / total_value) if total_value != 0 else 0.0

        cost_sum = sector_cost_sum[sector]
        profit_rate = float(sector_profit_amount_sum[sector] / cost_sum) if cost_sum != 0 else 0.0

        items.append(
            SectorAllocationItem(
                sector=sector,
                weight=weight,
                profitRate=profit_rate,
            )
        )

    items.sort(key=lambda x: x.weight, reverse=True)

    return SectorAllocationResponse(
        totalSectors=len(items),
        sectors=items,
    )