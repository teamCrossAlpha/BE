from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal
from typing import List, Optional, Literal


class TradeCreateRequest(BaseModel):
    ticker: str = Field(min_length=1, max_length=16)
    tradeType: Literal["BUY", "SELL"]
    tradeDate: date
    price: Decimal = Field(gt=0)
    quantity: int = Field(gt=0)
    confidence: Optional[int] = Field(default=None, ge=0, le=100)
    behaviorType: str
    memo: Optional[str] = None


class TradeCreateResponse(BaseModel):
    tradeId: int
    status: str = "CREATED"


class TradeListItem(BaseModel):
    tradeId: int
    tradeDate: date
    ticker: str
    tradeType: Literal["BUY", "SELL"]
    price: float
    quantity: int
    pnlStatus: Literal["OPEN", "CLOSED"]
    pnl: Optional[PnlPayload] = None
    confidence: Optional[int] = None
    behaviorType: str
    memo: Optional[str] = None
    positionAction: Literal["ENTRY", "ADD", "PARTIAL_EXIT", "EXIT"]


class TradeListResponse(BaseModel):
    trades: List[TradeListItem] = Field(default_factory=list)


class PnlPayload(BaseModel):
    profitRate: float
    profitAmount: float


class TradeDetailResponse(BaseModel):
    tradeId: int
    ticker: str
    tradeType: Literal["BUY", "SELL"]
    tradeDate: date
    price: float
    quantity: int
    confidence: Optional[int] = None
    behaviorType: str
    memo: Optional[str] = None
    pnlStatus: Literal["OPEN", "CLOSED"]
    pnl: Optional[PnlPayload] = None
    averagePrice: Optional[float] = None


class TradeSummaryPayload(BaseModel):
    totalTrades: int
    winRate: float
    averageConfidence: int
    bestTradeReturn: float


class TradeSummaryResponse(BaseModel):
    summary: TradeSummaryPayload