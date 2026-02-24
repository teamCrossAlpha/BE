from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from portfolio.portfolio_repository import upsert_snapshot
from portfolio.portfolio_service import get_portfolio_summary


def run_daily_portfolio_snapshot_for_user(db: Session, user_id: int) -> None:
    """
    오늘 날짜 기준 포트폴리오 스냅샷 저장(upsert).
    - total_value: 필수
    - profit_rate/amount: avg 없는 종목만 있으면 None일 수 있음
    """
    today = date.today()

    summary = get_portfolio_summary(db, user_id)

    total_value = Decimal(str(summary.totalValue))

    total_profit_rate = (
        Decimal(str(summary.totalProfitRate))
        if summary.totalProfitRate is not None
        else None
    )

    total_profit_amount = (
        Decimal(str(summary.totalProfitAmount))
        if summary.totalProfitAmount is not None
        else None
    )

    upsert_snapshot(
        db=db,
        user_id=user_id,
        captured_date=today,
        total_value=total_value,
        total_profit_rate=total_profit_rate,
        total_profit_amount=total_profit_amount,
    )