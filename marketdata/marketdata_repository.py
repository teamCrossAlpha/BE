# marketdata/asset_price_repository.py
from __future__ import annotations

from sqlalchemy.orm import Session

from marketdata.marketdata_entity import AssetPrice


def get_asset_price_by_ticker(db: Session, ticker: str) -> AssetPrice | None:
    t = ticker.upper().strip()
    return db.query(AssetPrice).filter(AssetPrice.ticker == t).first()


def upsert_asset_price(
    db: Session,
    ticker: str,
    price,
    change=None,
    change_rate=None,
) -> AssetPrice:
    t = ticker.upper().strip()
    row = db.query(AssetPrice).filter(AssetPrice.ticker == t).first()

    if row is None:
        row = AssetPrice(
            ticker=t,
            price=price,
            change=change,
            change_rate=change_rate,
        )
        db.add(row)
    else:
        row.price = price
        row.change = change
        row.change_rate = change_rate

    db.flush()
    return row