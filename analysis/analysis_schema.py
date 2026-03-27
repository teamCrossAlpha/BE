from __future__ import annotations

from datetime import date
from typing import List, Literal, Optional

from pydantic import BaseModel


AnalysisRangeMonthly = Literal["6M", "1Y", "ALL"]
AnalysisRangeCumulative = Literal["1M", "3M", "6M", "1Y", "YTD", "ALL"]


class MonthlyPerformanceItem(BaseModel):
    yearMonth: str
    returnRate: float
    tradeCount: int


class MonthlyPerformanceResponse(BaseModel):
    range: AnalysisRangeMonthly
    totalTrades: int
    monthlyPerformance: List[MonthlyPerformanceItem]


class CumulativeProfitPoint(BaseModel):
    date: str
    profit: float


class CumulativeProfitResponse(BaseModel):
    range: AnalysisRangeCumulative
    totalTrades: int
    finalProfit: float
    maxProfit: float
    minProfit: float
    series: List[CumulativeProfitPoint]


class SectorAllocationItem(BaseModel):
    sector: str
    weight: float
    profitRate: Optional[float] = None


class SectorAllocationResponse(BaseModel):
    totalSectors: int
    sectors: List[SectorAllocationItem]