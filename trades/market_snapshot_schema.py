from __future__ import annotations
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# 공통
SnapshotType = Literal["quant", "qual"]
QuantRange = Literal["3M", "6M", "1Y"]


class PricePoint(BaseModel):
    date: str
    close: float


class BollingerDTO(BaseModel):
    upper: float
    middle: float
    lower: float


class IndicatorsDTO(BaseModel):
    sma20: float
    sma50: float
    rsi14: float
    bollinger: BollingerDTO


class SignalItem(BaseModel):
    id: str
    title: str
    description: str
    strength: Literal["LOW", "MEDIUM", "HIGH"]


# Quant 응답
class TradeMarketSnapshotQuantResponse(BaseModel):
    type: Literal["quant"] = "quant"
    range: QuantRange
    priceSeries: List[PricePoint]
    indicators: IndicatorsDTO
    signals: List[SignalItem]
    summaryText: Optional[str] = None


# Qual 응답
class TradeMarketSnapshotNewsItem(BaseModel):
    title: str
    summary: str
    source: str
    url: str
    publishedAt: str | None = None


class TradeMarketSnapshotQualResponse(BaseModel):
    type: Literal["qual"] = "qual"
    snapshotDate: str
    news: List[TradeMarketSnapshotNewsItem]
