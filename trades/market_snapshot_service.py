from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Literal

import pandas as pd
import requests
from fastapi import HTTPException
from sqlalchemy.orm import Session

from common.config import settings
from tickers.gpt_interpreter import explain_snapshot_with_openai  # tech 목적용
from tickers.tickers_schema import BollingerBands, TechnicalIndicators, TechnicalSnapshot
from trades.market_snapshot_schema import (
    TradeMarketSnapshotQuantResponse,
    IndicatorsDTO,
    BollingerDTO,
    PricePoint,
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


@dataclass
class DailyBar:
    date: str
    close: float


def _fetch_daily_series_compact(ticker: str) -> List[DailyBar]:
    """
    TIME_SERIES_DAILY + compact(최근 100개)
    """
    data = _alpha_vantage_get(
        {
            "function": "TIME_SERIES_DAILY",
            "symbol": ticker,
            "outputsize": "compact",
        }
    )
    ts = data.get("Time Series (Daily)")
    if not ts:
        raise RuntimeError(f"AlphaVantage 응답에 Time Series (Daily) 없음: {data}")

    bars: List[DailyBar] = []
    for d, row in ts.items():
        c = row.get("4. close")
        if c is None:
            continue
        bars.append(DailyBar(date=d, close=float(c)))

    bars.sort(key=lambda b: b.date)
    return bars


def _to_dataframe(bars: List[DailyBar]) -> pd.DataFrame:
    df = pd.DataFrame([{"date": b.date, "close": b.close} for b in bars])
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()
    return df


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

def build_quant_snapshot_for_trade(db: Session, trade: Trade, rng: QuantRange) -> TradeMarketSnapshotQuantResponse:
    ticker = trade.ticker.upper().strip()
    trade_day: date = trade.trade_date

    bars = _fetch_daily_series_compact(ticker)
    df = _to_dataframe(bars)

    # trade_date 이전까지만 사용 (해당 날짜가 휴장일이면 가장 가까운 이전 거래일 기준으로 자동 슬라이싱됨)
    df = df[df.index.date <= trade_day]
    if df.empty:
        raise HTTPException(status_code=422, detail="거래일 이전 가격 데이터가 없습니다.")

    # range 기준으로 컷
    days = _range_to_days(rng)
    cutoff = datetime.combine(trade_day, datetime.min.time()) - timedelta(days=days * 2)  # 주말/휴장 여유
    df = df[df.index >= cutoff]
    if df.empty:
        raise HTTPException(status_code=422, detail="해당 range 구간에 데이터가 없습니다.")

    # indicators 계산(최소 50거래일 필요)
    try:
        df_calc, indicators = _calc_indicators(df)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # priceSeries는 차트 렌더링용으로 최근 N개 (range별로 다르게)
    # 3M: ~70개, 6M: ~120개(근데 compact 100 제한이라 최대 100), 1Y: 거의 부족할 수 있음
    max_points = 70 if rng == "3M" else 100
    recent = df_calc.tail(max_points)

    price_series = [
        PricePoint(date=idx.strftime("%Y-%m-%d"), close=float(row["close"]))
        for idx, row in recent.iterrows()
    ]

    resp = TradeMarketSnapshotQuantResponse(
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
    )
    return resp


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