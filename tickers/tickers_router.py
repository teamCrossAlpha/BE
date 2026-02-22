from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from common.database import get_db
from tickers.tickers_schema import ChartResponse, QuoteResponse, TechnicalSummaryResponse
from tickers.tickers_service import (
    get_chart_1m,
    get_quote,
    get_technical_summary_with_llm,
)
from typing import Literal

router = APIRouter(prefix="/api/tickers", tags=["TICKERS"])


@router.get("/{ticker}/quote", response_model=QuoteResponse)
def get_ticker_quote(
    ticker: str,
    db: Session = Depends(get_db),
):
    return get_quote(db, ticker)


@router.get("/{ticker}/chart", response_model=ChartResponse)
def get_ticker_chart(
    ticker: str,
):
    # 스펙: 1M 고정
    return get_chart_1m(ticker)


@router.get("/{ticker}/technical-summary", response_model=TechnicalSummaryResponse)
def get_ticker_technical_summary(
    ticker: str,
    range: Literal["3M","6M","1Y"] = Query("3M"),
):
    return get_technical_summary_with_llm(ticker, rng=range)