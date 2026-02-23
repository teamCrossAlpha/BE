from pydantic import BaseModel
from typing import List


class BuyPatternItem(BaseModel):
    tag: str
    label: str
    count: int
    winRate: float
    averageReturn: float


class BuyPatternResponse(BaseModel):
    totalCompletedTrades: int
    patterns: List[BuyPatternItem]