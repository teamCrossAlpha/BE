from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from analysis.analysis_schema import (
    MonthlyPerformanceResponse,
    CumulativeProfitResponse,
    SectorAllocationResponse,
)
from analysis.analysis_service import (
    get_monthly_performance,
    get_cumulative_profit,
    get_sector_allocation,
)
from common.database import get_db
from common.dependencies import get_current_user_id

router = APIRouter(prefix="/api/analysis", tags=["Analysis"])


@router.get("/monthly-performance", response_model=MonthlyPerformanceResponse)
def read_monthly_performance(
    range: str = Query("6M"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return get_monthly_performance(db, user_id, rng=range)


@router.get("/cumulative-profit", response_model=CumulativeProfitResponse)
def read_cumulative_profit(
    range: str = Query("3M"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return get_cumulative_profit(db, user_id, rng=range)


@router.get("/sector-allocation", response_model=SectorAllocationResponse)
def read_sector_allocation(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return get_sector_allocation(db, user_id)