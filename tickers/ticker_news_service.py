import datetime as dt
from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from tickers.ticker_news_entity import TickerNews
from tickers.tickers_entity import Ticker
from tickers.tickers_schema import (
    TickerNewsResponse,
    TickerNewsItem,
)


def get_ticker_news(db: Session, ticker: str) -> TickerNewsResponse:
    """
    개별 종목 뉴스 조회
    - 가장 최신 snapshot_date 기준
    - 뉴스 최대 3개 반환
    """

    t = ticker.upper().strip()

    ticker_obj = db.query(Ticker).filter(Ticker.ticker == t).first()
    if not ticker_obj:
        raise HTTPException(status_code=404, detail="존재하지 않는 종목입니다.")

    # 가장 최신 스냅샷 날짜 조회
    latest_snapshot = (
        db.query(TickerNews.snapshot_date)
        .filter(TickerNews.ticker_id == ticker_obj.id)
        .order_by(TickerNews.snapshot_date.desc())
        .first()
    )

    if not latest_snapshot:
        return TickerNewsResponse(
            ticker=t,
            snapshotDate="",
            news=[]
        )

    snapshot_date = latest_snapshot[0]

    rows: List[TickerNews] = (
        db.query(TickerNews)
        .filter(
            TickerNews.ticker_id == ticker_obj.id,
            TickerNews.snapshot_date == snapshot_date
        )
        .order_by(TickerNews.published_at.desc())
        .limit(3)
        .all()
    )

    return TickerNewsResponse(
        ticker=t,
        snapshotDate=str(snapshot_date),
        news=[
            TickerNewsItem(
                title=row.title,
                summary=row.summary,
                source=row.source,
                url=row.url,
                publishedAt=row.published_at.isoformat() if row.published_at else None
            )
            for row in rows
        ]
    )