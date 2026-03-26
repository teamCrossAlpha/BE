from __future__ import annotations

import time
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Literal

import yfinance as yf
import pandas as pd
import requests
from fastapi import HTTPException
from sqlalchemy.orm import Session

from common.config import settings
from tickers.gpt_interpreter import explain_snapshot_with_openai
from tickers.ticker_news_entity import TickerNews
from tickers.tickers_entity import Ticker
from tickers.tickers_schema import BollingerBands, TechnicalIndicators, TechnicalSnapshot
from tickers.tickers_service import _make_signal_ids
from trades.market_snapshot_schema import (
    TradeMarketSnapshotQuantResponse,
    IndicatorsDTO,
    BollingerDTO,
    PricePoint,
    TradeMarketSnapshotNewsItem,
    TradeMarketSnapshotQualResponse,
    SignalItem,
)
from trades.trades_entity import Trade, TradeMarketSnapshot


QuantRange = Literal["3M", "6M", "1Y"]

# AlphaVantage 유틸

def _alpha_vantage_api_key() -> str:
    key = getattr(settings, "alpha_vantage_tech_api_key", None) or getattr(settings, "alpha_vantage_api_key", None)
    if not key:
        raise RuntimeError("alpha_vantage_tech_api_key(or alpha_vantage_api_key)가 설정되어 있지 않습니다.")
    return key


def _alpha_vantage_get(params: Dict[str, Any]) -> Dict[str, Any]:
    time.sleep(1.05)

    url = "https://www.alphavantage.co/query"
    params = {**params, "apikey": _alpha_vantage_api_key()}
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()

    if "Error Message" in data:
        raise RuntimeError(f"AlphaVantage Error: {data['Error Message']}")
    if "Note" in data:
        raise RuntimeError(f"AlphaVantage Rate limit: {data['Note']}")
    if "Information" in data:
        raise RuntimeError(f"AlphaVantage Info: {data['Information']}")

    return data


def _safe_float(v: Any) -> Optional[float]:
    try:
        if v is None:
            return None
        s = str(v).strip()
        if s == "" or s.lower() in ("none", "null", "nan"):
            return None
        return float(s)
    except Exception:
        return None


def _fetch_daily_series_yf(ticker: str, trade_day: date, rng: str) -> pd.DataFrame:
    """
    yfinance로 일봉 종가 데이터 조회
    - trade_day 이전 데이터까지만 사용하기 위해 end는 trade_day + 1일
    - 지표 계산 여유분 확보 위해 range보다 넉넉하게 조회
    """
    rng = (rng or "3M").upper().strip()

    if rng == "3M":
        lookback_days = 120
    elif rng == "6M":
        lookback_days = 240
    elif rng == "1Y":
        lookback_days = 420
    else:
        lookback_days = 120

    start_day = trade_day - timedelta(days=lookback_days)
    end_day = trade_day + timedelta(days=1)

    df = yf.download(
        ticker,
        start=start_day.strftime("%Y-%m-%d"),
        end=end_day.strftime("%Y-%m-%d"),
        interval="1d",
        auto_adjust=False,
        progress=False,
    )

    if df is None or df.empty:
        raise ValueError("yfinance에서 가격 데이터를 가져오지 못했습니다.")

    # MultiIndex 방어
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]

    if "Close" not in df.columns:
        raise ValueError("yfinance 응답에 Close 컬럼이 없습니다.")

    out = df[["Close"]].copy()
    out = out.rename(columns={"Close": "close"})
    out.index = pd.to_datetime(out.index)
    out = out.sort_index()

    # trade_day 이후 데이터 제거
    out = out[out.index.date <= trade_day]

    if out.empty:
        raise ValueError("거래일 이전 가격 데이터가 없습니다.")

    return out


def _convert_signals(raw_signals: List[Any]) -> List[SignalItem]:
    items: List[SignalItem] = []

    for s in raw_signals or []:
        try:
            items.append(
                SignalItem(
                    id=str(getattr(s, "id", "")),
                    title=str(getattr(s, "title", "")),
                    description=str(getattr(s, "description", "")),
                    strength=str(getattr(s, "strength", "LOW")).upper(),
                )
            )
        except Exception:
            continue

    return items


# 지표 계산(기존 tickers_service와 동일 로직)

def _calc_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def _calc_indicators(df: pd.DataFrame) -> Tuple[pd.DataFrame, TechnicalIndicators]:
    out = df.copy()
    out["sma20"] = out["close"].rolling(20).mean()
    out["sma50"] = out["close"].rolling(50).mean()
    out["rsi14"] = _calc_rsi(out["close"], 14)

    mid = out["close"].rolling(20).mean()
    std = out["close"].rolling(20).std()
    out["bb_mid"] = mid
    out["bb_upper"] = mid + 2 * std
    out["bb_lower"] = mid - 2 * std

    out = out.dropna()
    if out.empty:
        raise ValueError("지표 계산을 위한 데이터가 부족합니다(최소 50거래일 이상 필요).")

    last = out.iloc[-1]
    indicators = TechnicalIndicators(
        sma20=float(last["sma20"]),
        sma50=float(last["sma50"]),
        rsi14=float(last["rsi14"]),
        bollinger=BollingerBands(
            upper=float(last["bb_upper"]),
            middle=float(last["bb_mid"]),
            lower=float(last["bb_lower"]),
        ),
    )
    return out, indicators


def _range_to_days(rng: QuantRange) -> int:
    if rng == "3M":
        return 93
    if rng == "6M":
        return 186
    return 366  # 1Y


# 캐시 조회/저장

def _get_cached_snapshot(
    db: Session,
    trade_id: int,
    type_: Literal["quant", "qual"],
    rng: Optional[str],
) -> Optional[TradeMarketSnapshot]:
    q = db.query(TradeMarketSnapshot).filter(
        TradeMarketSnapshot.trade_id == trade_id,
        TradeMarketSnapshot.type == type_,
    )
    if rng is None:
        q = q.filter(TradeMarketSnapshot.range.is_(None))
    else:
        q = q.filter(TradeMarketSnapshot.range == rng)
    return q.first()


def _save_snapshot(
    db: Session,
    trade_id: int,
    type_: Literal["quant", "qual"],
    rng: Optional[str],
    data: Dict[str, Any],
) -> TradeMarketSnapshot:
    row = TradeMarketSnapshot(
        trade_id=trade_id,
        type=type_,
        range=rng,
        data=data,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


# Quant 생성 (trade_date 기준)

def build_quant_snapshot_for_trade(db: Session, trade: Trade, rng: str) -> TradeMarketSnapshotQuantResponse:
    ticker = trade.ticker.upper().strip()
    trade_day: date = trade.trade_date
    rng = (rng or "3M").upper().strip()

    df = _fetch_daily_series_yf(ticker, trade_day, rng)

    # 차트용 series
    price_series = [
        PricePoint(date=idx.strftime("%Y-%m-%d"), close=float(row["close"]))
        for idx, row in df.iterrows()
    ]

    # 기술지표 계산
    df_calc, indicators = _calc_indicators(df)
    signal_ids = _make_signal_ids(df_calc, indicators)

    signals: List[SignalItem] = []
    summary_text: str | None = None

    try:
        snapshot = TechnicalSnapshot(
            ticker=ticker,
            range=rng,
            lastClose=float(df_calc.iloc[-1]["close"]),
            indicators=indicators,
            signalIds=signal_ids,
        )
        explain = explain_snapshot_with_openai(snapshot, purpose="tech")
        signals = _convert_signals(explain.signals)
        summary_text = explain.summaryText
    except Exception:
        pass

    return TradeMarketSnapshotQuantResponse(
        type="quant",
        range=rng,
        priceSeries=price_series,
        indicators=IndicatorsDTO(
            sma20=indicators.sma20,
            sma50=indicators.sma50,
            rsi14=indicators.rsi14,
            bollinger=BollingerDTO(
                upper=indicators.bollinger.upper,
                middle=indicators.bollinger.middle,
                lower=indicators.bollinger.lower,
            ),
        ),
        signals=signals,
        summaryText=summary_text,
    )


def build_qual_snapshot_for_trade(db: Session, trade: Trade) -> TradeMarketSnapshotQualResponse:
    ticker_str = trade.ticker.upper().strip()
    trade_day: date = trade.trade_date

    ticker_obj = db.query(Ticker).filter(Ticker.ticker == ticker_str).first()
    if not ticker_obj:
        raise HTTPException(status_code=404, detail="ticker not found")

    rows = (
        db.query(TickerNews)
        .filter(
            TickerNews.ticker_id == ticker_obj.id,
            TickerNews.snapshot_date == trade_day,
        )
        .order_by(TickerNews.published_at.desc())
        .limit(3)
        .all()
    )

    news_items = [
        TradeMarketSnapshotNewsItem(
            title=row.title,
            summary=row.summary or "",
            source=row.source or "",
            url=row.url or "",
            publishedAt=row.published_at.isoformat() if row.published_at else None,
        )
        for row in rows
    ]

    return TradeMarketSnapshotQualResponse(
        type="qual",
        snapshotDate=str(trade_day),
        news=news_items,
    )


# service 함수들

def get_trade_snapshot_quant(db: Session, user_id: int, trade_id: int, rng: QuantRange) -> TradeMarketSnapshotQuantResponse:
    trade = db.query(Trade).filter(Trade.id == trade_id, Trade.user_id == user_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="trade not found")

    cached = _get_cached_snapshot(db, trade_id, "quant", rng)
    if cached:
        # DB에 JSON으로 들어간 걸 응답 스키마로 검증/반환
        return TradeMarketSnapshotQuantResponse.model_validate(cached.data)

    # 생성
    resp = build_quant_snapshot_for_trade(db, trade, rng)
    _save_snapshot(db, trade_id, "quant", rng, resp.model_dump())
    return resp


def get_trade_snapshot_qual(db: Session, user_id: int, trade_id: int) -> TradeMarketSnapshotQualResponse:
    trade = (
        db.query(Trade)
        .filter(Trade.id == trade_id, Trade.user_id == user_id)
        .first()
    )
    if not trade:
        raise HTTPException(status_code=404, detail="trade not found")

    cached = _get_cached_snapshot(db, trade_id, "qual", None)
    if cached:
        return TradeMarketSnapshotQualResponse.model_validate(cached.data)

    resp = build_qual_snapshot_for_trade(db, trade)
    _save_snapshot(db, trade_id, "qual", None, resp.model_dump())
    return resp