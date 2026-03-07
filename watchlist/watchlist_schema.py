from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class WatchlistItem(BaseModel):
    ticker: str
    addedAt: datetime


class WatchlistListResponse(BaseModel):
    watchlistTickers: List[WatchlistItem] = Field(default_factory=list)


class WatchlistCreateRequest(BaseModel):
    ticker: str = Field(..., max_length=16)


class WatchlistCreateResponse(BaseModel):
    status: str  # "SUCCESS"
    ticker: str
    addedAt: datetime


class WatchlistDeleteResponse(BaseModel):
    status: str  # "DELETED"
    ticker: str