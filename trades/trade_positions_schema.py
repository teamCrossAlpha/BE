from __future__ import annotations

from datetime import date, datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class PnlPayload(BaseModel):
    profitRate: float
    profitAmount: float


class PositionTradeItem(BaseModel):
    tradeId: int
    tradeDate: date
    tradeType: Literal["BUY", "SELL"]
    positionAction: Literal["ENTRY", "ADD", "PARTIAL_EXIT", "EXIT"]
    price: float
    quantity: int
    pnl: Optional[PnlPayload] = None  # SELL이면 값, BUY이면 null


class OpenPositionItem(BaseModel):
    positionId: int
    ticker: str

    holdingQuantity: int
    averagePrice: Optional[float] = None

    totalTrades: int = 0  # 이 포지션에 속한 trades 개수

    pnl: Optional[PnlPayload] = None  # 보유분 기준(미실현) PnL

    openedAt: datetime
    trades: List[PositionTradeItem] = Field(default_factory=list)


class ClosedPositionItem(BaseModel):
    positionId: int
    ticker: str

    totalBuyQuantity: int
    averagePrice: Optional[float] = None  # (가중)평균매입단가

    totalTrades: int = 0

    pnl: Optional[PnlPayload] = None  # 실현 손익(SELL pnl 합산)

    openedAt: datetime
    closedAt: Optional[datetime] = None
    trades: List[PositionTradeItem] = Field(default_factory=list)


class TradePositionsResponse(BaseModel):
    status: Literal["OPEN", "CLOSED"]
    openPositions: List[OpenPositionItem] = Field(default_factory=list)
    closedPositions: List[ClosedPositionItem] = Field(default_factory=list)