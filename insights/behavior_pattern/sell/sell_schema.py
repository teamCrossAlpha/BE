from pydantic import BaseModel
from typing import List


class SellPatternItem(BaseModel):
    tag: str
    label: str
    count: int
    winRate: float
    averageReturn: float


class SellPatternResponse(BaseModel):
    totalSellTrades: int
    patterns: List[SellPatternItem]