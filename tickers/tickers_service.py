from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import requests
from sqlalchemy.orm import Session

from common.config import settings
from marketdata.marketdata_service import get_cached_quote_fields
from tickers.gpt_interpreter import explain_snapshot_with_openai
from tickers.tickers_schema import (
    BollingerBands,
    ChartPoint,
    ChartResponse,
    QuoteResponse,
    TechnicalIndicators,
    TechnicalSnapshot,
    TechnicalSummaryResponse,
)
from trades.trades_entity import Asset


# =========================
# AlphaVantage 공통 유틸
# =========================

def _alpha_vantage_api_key() -> str:
    key = getattr(settings, "alpha_vantage_tech_api_key", None)
    if not key:
        raise RuntimeError("alpha_vantage_api_key가 설정되어 있지 않습니다.")
    return key


def _alpha_vantage_get(params: Dict[str, Any]) -> Dict[str, Any]:
    url = "https://www.alphavantage.co/query"
    params = {**params, "apikey": _alpha_vantage_api_key()}
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()

    if "Error Message" in data:
        raise ValueError(f"AlphaVantage Error: {data['Error Message']}")
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


# =========================
# 시세/차트 공통 타입
# =========================

@dataclass
class AlphaVantageDailyBar:
    date: str
    close: float


def _fetch_daily_series(ticker: str, outputsize: str = "compact") -> List[AlphaVantageDailyBar]:
    """
    AlphaVantage TIME_SERIES_DAILY
    - outputsize: 'compact'(최근 100일) / 'full'(최대)
    """
    data = _alpha_vantage_get(
        {
            "function": "TIME_SERIES_DAILY",
            "symbol": ticker,
            "outputsize": outputsize,
        }
    )

    ts = data.get("Time Series (Daily)")
    if not ts:
        raise ValueError(f"AlphaVantage 응답에 Time Series (Daily) 없음: {data}")

    bars: List[AlphaVantageDailyBar] = []
    for date_str, row in ts.items():
        close_str = row.get("4. close")
        if close_str is None:
            continue
        bars.append(AlphaVantageDailyBar(date=date_str, close=float(close_str)))

    bars.sort(key=lambda b: b.date)  # 오름차순
    return bars


def _to_dataframe(bars: List[AlphaVantageDailyBar]) -> pd.DataFrame:
    df = pd.DataFrame([{"date": b.date, "close": b.close} for b in bars])
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()
    return df


# =========================
# 기술지표 계산
# =========================

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


def _make_signal_ids(df_calc: pd.DataFrame, indicators: TechnicalIndicators) -> List[str]:
    ids: List[str] = []

    # SMA 방향
    ids.append("SMA_BEARISH" if indicators.sma20 < indicators.sma50 else "SMA_BULLISH")

    # RSI 구간
    if indicators.rsi14 <= 40:
        ids.append("RSI_OVERSOLD_NEAR")
    elif indicators.rsi14 >= 70:
        ids.append("RSI_OVERBOUGHT")
    else:
        ids.append("RSI_NEUTRAL")

    # 가격 위치(볼린저)
    last_close = float(df_calc.iloc[-1]["close"])
    if last_close <= indicators.bollinger.lower:
        ids.append("BB_NEAR_LOWER")
    elif last_close >= indicators.bollinger.upper:
        ids.append("BB_NEAR_UPPER")
    else:
        ids.append("BB_MIDDLE_ZONE")

    return ids


def _range_to_days(rng: str) -> int:
    rng = (rng or "").upper()
    if rng == "1M":
        return 31
    if rng == "3M":
        return 93
    if rng == "6M":
        return 186
    if rng == "1Y":
        return 366
    return 93  # default 3M


# =========================
# 1) technical-summary (LLM 포함)
# =========================

def get_technical_summary_with_llm(ticker: str, rng: str = "3M") -> TechnicalSummaryResponse:

    t = ticker.upper().strip()
    rng = (rng or "3M").upper().strip()

    if rng == "1M":
        raise ValueError("technical-summary는 1M을 지원하지 않습니다. (최소 3M)")

    days = _range_to_days(rng)

    outputsize = "compact"

    bars = _fetch_daily_series(t, outputsize=outputsize)
    df = _to_dataframe(bars)

    cutoff = datetime.today() - timedelta(days=days * 2)
    df = df[df.index >= cutoff]

    if df.empty:
        raise ValueError("해당 range 구간에 데이터가 없습니다.")

    df_calc, indicators = _calc_indicators(df)
    signal_ids = _make_signal_ids(df_calc, indicators)

    resp = TechnicalSummaryResponse(
        ticker=t,
        range=rng,
        indicators=indicators,
        signals=[],
        summaryText=None,
    )

    try:
        snapshot = TechnicalSnapshot(
            ticker=t,
            range=rng,
            lastClose=float(df_calc.iloc[-1]["close"]),
            indicators=indicators,
            signalIds=signal_ids,
        )
        explain = explain_snapshot_with_openai(snapshot, purpose="tech")
        resp.signals = explain.signals
        resp.summaryText = explain.summaryText
    except Exception:
        pass

    return resp


# =========================
# 2) assets 메타데이터 (OVERVIEW) -> upsert
# =========================

def get_or_create_asset_minimal(db: Session, ticker: str) -> Asset:
    """
    -외부 API 호출 없이 assets row만 보장
    -없으면 name=ticker 로 최소 insert
    """
    t = ticker.upper().strip()
    asset = db.query(Asset).filter(Asset.ticker == t).first()
    if asset:
        return asset

    asset = Asset(
        ticker=t,
        name=t,
        currency=None,
        market_cap=None,
        meta_updated_at=None,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _is_meta_stale(asset: Asset, ttl_hours: int = 24) -> bool:
    """
    meta_updated_at이 없거나 ttl_hours(기본 24시간) 지났으면 stale
    비교는 UTC aware 기준으로 통일
    """
    last = getattr(asset, "meta_updated_at", None)
    if last is None:
        return True

    # last가 naive로 들어온 경우(기존 데이터) -> UTC로 간주해서 tzinfo 붙여 방어
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)

    return (_utcnow() - last) >= timedelta(hours=ttl_hours)


def refresh_asset_overview_if_needed(db: Session, asset: Asset, ttl_hours: int = 24) -> None:
    """
    - ttl_hours(기본 24시간)에 한 번만 OVERVIEW로 메타 갱신
    - 실패하면 return
    """
    if not _is_meta_stale(asset, ttl_hours=ttl_hours):
        return

    overview = _fetch_overview(asset.ticker)
    if not overview:
        return

    name = overview.get("Name")
    currency = overview.get("Currency")
    market_cap = _safe_float(overview.get("MarketCapitalization"))
    sector = overview.get("Sector")

    # 빈 값만 보정(기존 값 있으면 유지)
    if name and (asset.name is None or asset.name.strip() == "" or asset.name == asset.ticker):
        asset.name = name

    if currency and (asset.currency is None or str(asset.currency).strip() == ""):
        asset.currency = currency

    if market_cap is not None and asset.market_cap is None:
        asset.market_cap = market_cap

    if sector and (getattr(asset, "sector", None) is None or str(asset.sector).strip() == ""):
        asset.sector = sector

    asset.meta_updated_at = _utcnow()
    db.commit()
    db.refresh(asset)


def _fetch_overview(ticker: str) -> Dict[str, Any]:

    try:
        return _alpha_vantage_get({"function": "OVERVIEW", "symbol": ticker}) or {}
    except Exception:
        return {}


# =========================
# 3) quote (GLOBAL_QUOTE)
# =========================

def _fetch_global_quote(ticker: str) -> Dict[str, Any]:
    data = _alpha_vantage_get({"function": "GLOBAL_QUOTE", "symbol": ticker})
    q = data.get("Global Quote")
    if not q:
        raise ValueError(f"GLOBAL_QUOTE 응답이 비어있습니다: {data}")
    return q


def get_quote(db: Session, ticker: str) -> QuoteResponse:
    t = ticker.upper().strip()

    # 1) 가격 캐시에서 조회 (없거나 stale이면 yfinance로 갱신)
    price_row = get_cached_quote_fields(db, t,ttl_seconds=180)

    price = float(price_row.price)
    change = float(price_row.change) if price_row.change is not None else 0.0
    change_rate = float(price_row.change_rate) if price_row.change_rate is not None else 0.0

    # 2) 메타는 assets 테이블
    asset = get_or_create_asset_minimal(db, t)

    return QuoteResponse(
        ticker=t,
        name=getattr(asset, "name", None),
        price=price,
        change=change,
        changeRate=change_rate,
        currency=getattr(asset, "currency", None),
        sector=getattr(asset, "sector", None),
        marketCap=float(asset.market_cap) if getattr(asset, "market_cap", None) is not None else None,
    )


# =========================
# 4) chart (1M 고정)
# =========================

def get_chart_1m(ticker: str) -> ChartResponse:
    t = ticker.upper().strip()

    bars = _fetch_daily_series(t, outputsize="compact")

    # 거래일 기준 대략 1개월 커버하도록 40개 정도만 자름
    recent = bars[-40:] if len(bars) > 40 else bars
    series = [ChartPoint(date=b.date, close=b.close) for b in recent]

    return ChartResponse(ticker=t, range="1M", series=series)