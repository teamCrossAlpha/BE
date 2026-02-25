from pydantic import BaseModel
from typing import List


class SellTradeInfo(BaseModel):
    date: str


class CompletedTrade(BaseModel):
    ticker: str
    confidence: int
    pnlPercent: float
    sellTrade: SellTradeInfo


class ConfidenceScatterResponse(BaseModel):
    totalCompletedTrades: int
    trades: List[CompletedTrade]