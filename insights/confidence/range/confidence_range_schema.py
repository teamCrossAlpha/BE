from pydantic import BaseModel
from typing import List


class ConfidenceZone(BaseModel):
    rangeLabel: str
    tradeCount: int
    averageReturn: float
    winRate: float


class BestZoneSummary(BaseModel):
    bestRange: str
    averageReturn: float
    winRate: float
    message: str


class ConfidenceRangeResponse(BaseModel):
    totalCompletedTrades: int
    zones: List[ConfidenceZone]
    bestZone: BestZoneSummary