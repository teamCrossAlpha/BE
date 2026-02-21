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


# Quant 응답
class TradeMarketSnapshotQuantResponse(BaseModel):
    type: Literal["quant"] = "quant"
    range: QuantRange
    priceSeries: List[PricePoint]
    indicators: IndicatorsDTO
