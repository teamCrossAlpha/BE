# marketdata/asset_price_service.py
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from marketdata.marketdata_repository import get_asset_price_by_ticker, upsert_asset_price
from marketdata.yfinance_provider import fetch_quote_fields


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _is_stale(updated_at: datetime | None, ttl_seconds: int) -> bool:
    if updated_at is None:
        return True
    if updated_at.tzinfo is None:
        updated_at = updated_at.replace(tzinfo=timezone.utc)
    return (_utcnow() - updated_at) >= timedelta(seconds=ttl_seconds)


def get_cached_quote_fields(db: Session, ticker: str, ttl_seconds: int = 180):
    """
    - ttl_seconds 기본 180초(3분)
    - stale이면 yfinance 호출 후 asset_prices 업서트
    - 아니면 DB 값 그대로 반환
    """
    t = ticker.upper().strip()
    row = get_asset_price_by_ticker(db, t)

    if row is None or _is_stale(getattr(row, "updated_at", None), ttl_seconds):
        q = fetch_quote_fields(t)  # yfinance 호출
        row = upsert_asset_price(
            db,
            t,
            price=q.price,
            change=q.change,
            change_rate=q.change_rate,
        )
        db.commit()
        db.refresh(row)

    return row