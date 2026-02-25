from pydantic import BaseModel
from typing import List


class BuyPatternItem(BaseModel):
    tag: str
    label: str
    count: int


class BuyPatternResponse(BaseModel):
    totalBuyTrades: int
    patterns: List[BuyPatternItem]