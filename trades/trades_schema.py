from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal
from typing import Optional, Literal


class TradeCreateRequest(BaseModel):
    ticker: str = Field(min_length=1, max_length=16)
    tradeType: Literal["BUY", "SELL"]
    tradeDate: date
    price: Decimal = Field(gt=0)
    quantity: int = Field(gt=0)
    confidence: Optional[int] = Field(default=None, ge=0, le=100)
    behaviorType: str
    memo: Optional[str] = None