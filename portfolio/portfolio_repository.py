from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import func

from typing import Optional,List
from datetime import date
from decimal import Decimal

from trades.trades_entity import Holding
from portfolio.portfolio_entity import PortfolioSnapshot

def list_holdings_by_user(db: Session, user_id: int) -> list[Holding]:
    return (
        db.query(Holding)
        .filter(Holding.user_id == user_id)
        .all()
    )


def get_holding_by_user_ticker(db: Session, user_id: int, ticker: str) -> Optional[Holding]:
    t = ticker.upper().strip()
    return db.query(Holding).filter(Holding.user_id == user_id, Holding.ticker == t).first()


def create_holding(db: Session, holding: Holding) -> Holding:
    db.add(holding)
    db.flush()
    return holding


def delete_holding(db: Session, holding: Holding) -> None:
    db.delete(holding)
    db.flush()


def get_snapshot_by_date(db: Session, user_id: int, captured_date: date) -> Optional[PortfolioSnapshot]:
    return (
        db.query(PortfolioSnapshot)
        .filter(PortfolioSnapshot.user_id == user_id, PortfolioSnapshot.captured_date == captured_date)
        .first()
    )


def upsert_snapshot(
    db: Session,
    user_id: int,
    captured_date: date,
    total_value: Decimal,
    total_profit_rate: Decimal | None,
    total_profit_amount: Decimal | None,
) -> None:
    stmt = insert(PortfolioSnapshot).values(
        user_id=user_id,
        captured_date=captured_date,
        total_value=total_value,
        total_profit_rate=total_profit_rate,
        total_profit_amount=total_profit_amount,
    )

    stmt = stmt.on_conflict_do_update(
        index_elements=["user_id", "captured_date"],
        set_={
            "total_value": stmt.excluded.total_value,
            "total_profit_rate": stmt.excluded.total_profit_rate,
            "total_profit_amount": stmt.excluded.total_profit_amount,
            "updated_at": func.now(),
        },
    )

    db.execute(stmt)


def list_snapshots_range(db: Session, user_id: int, from_date: date, to_date: date) -> List[PortfolioSnapshot]:
    return (
        db.query(PortfolioSnapshot)
        .filter(
            PortfolioSnapshot.user_id == user_id,
            PortfolioSnapshot.captured_date >= from_date,
            PortfolioSnapshot.captured_date <= to_date,
        )
        .order_by(PortfolioSnapshot.captured_date.asc())
        .all()
    )