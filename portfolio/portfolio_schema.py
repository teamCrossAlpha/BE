from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import date, datetime


class HoldingItem(BaseModel):
    ticker: str
    quantity: int
    averagePrice: Optional[float] = None
    currentPrice: Optional[float] = None
    profitRate: Optional[float] = None  # 예: 0.085 (8.5%)


class HoldingsListResponse(BaseModel):
    holdings: List[HoldingItem] = Field(default_factory=list)


class HoldingUpsertRequest(BaseModel):
    ticker: str = Field(..., max_length=16)
    quantity: int = Field(..., ge=0)
    averagePrice: Optional[Decimal] = None  # null 허용


class HoldingUpsertResponse(BaseModel):
    status: str  # "SUCCESS"
    ticker: str
    quantity: int
    averagePrice: Optional[Decimal] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class HoldingDeleteResponse(BaseModel):
    status: str  # "DELETED"
    ticker: str


class PortfolioSummaryResponse(BaseModel):
    totalValue: float
    totalProfitRate: Optional[float] = None
    totalProfitAmount: Optional[float] = None


class PortfolioPerformancePoint(BaseModel):
    date: date
    value: float


class PortfolioPerformanceResponse(BaseModel):
    range: Literal["30D"] = "30D"
    series: List[PortfolioPerformancePoint] = Field(default_factory=list)