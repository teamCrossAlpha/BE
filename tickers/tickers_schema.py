from __future__ import annotations

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# -------------------------
# Chart
# -------------------------

class ChartPoint(BaseModel):
    date: str
    close: float


class ChartResponse(BaseModel):
    ticker: str
    range: str = "1M"
    series: List[ChartPoint]


# -------------------------
# Quote
# -------------------------

class QuoteResponse(BaseModel):
    ticker: str
    name: Optional[str] = None

    price: float
    change: float
    changeRate: float  # 예) 1.23 => 1.23%

    currency: Optional[str] = None
    sector: Optional[str] = None
    marketCap: Optional[float] = None


# -------------------------
# Technical Indicators
# -------------------------

class BollingerBands(BaseModel):
    upper: float
    middle: float
    lower: float


class TechnicalIndicators(BaseModel):
    sma20: float
    sma50: float
    rsi14: float
    bollinger: BollingerBands


# -------------------------
# LLM Explain (OpenAI output)
# -------------------------

Strength = Literal["LOW", "MEDIUM", "HIGH"]


class SignalItem(BaseModel):
    id: str
    title: str
    description: str
    strength: Strength


class ExplainResult(BaseModel):
    signals: List[SignalItem] = Field(default_factory=list)
    summaryText: Optional[str] = None


# -------------------------
# Snapshot passed to LLM
# -------------------------

class TechnicalSnapshot(BaseModel):
    ticker: str
    range: str
    lastClose: float
    indicators: TechnicalIndicators
    signalIds: List[str] = Field(default_factory=list)


# -------------------------
# API Response for technical-summary
# -------------------------

class TechnicalSummaryResponse(BaseModel):
    ticker: str
    range: str
    indicators: TechnicalIndicators
    signals: List[SignalItem] = Field(default_factory=list)
    summaryText: Optional[str] = None

# -------------------------
# News
# -------------------------

class TickerNewsItem(BaseModel):
    title: str
    summary: Optional[str]
    source: Optional[str]
    url: Optional[str]
    publishedAt: Optional[str]


class TickerNewsResponse(BaseModel):
    ticker: str
    snapshotDate: str
    news: List[TickerNewsItem]