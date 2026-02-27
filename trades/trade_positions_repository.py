from __future__ import annotations

from typing import List, Tuple

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import asc, desc

from trades.trades_entity import TradePosition, Trade, TradeResult


def list_positions(
    db: Session,
    user_id: int,
    status: str,
    sort: str = "recent",
) -> List[TradePosition]:
    q = (
        db.query(TradePosition)
        .options(joinedload(TradePosition.trades).joinedload(Trade.result))
        .filter(TradePosition.user_id == user_id, TradePosition.status == status)
    )

    is_recent = (sort or "recent").lower() == "recent"

    if status == "OPEN":
        q = q.order_by(desc(TradePosition.opened_at) if is_recent else asc(TradePosition.opened_at))
    else:
        # CLOSED는 closed_at이 항상 있다고 가정하지만, 혹시 NULL이면 opened_at으로 보조 정렬
        q = q.order_by(
            desc(TradePosition.closed_at) if is_recent else asc(TradePosition.closed_at),
            desc(TradePosition.opened_at) if is_recent else asc(TradePosition.opened_at),
        )

    return q.all()