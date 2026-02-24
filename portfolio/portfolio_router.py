from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from common.database import get_db
from common.dependencies import get_current_user_id

from portfolio.portfolio_schema import (
    HoldingsListResponse,
    HoldingUpsertRequest,
    HoldingUpdateRequest,
    HoldingUpsertResponse,
    HoldingDeleteResponse,
    PortfolioSummaryResponse, PortfolioPerformanceResponse,
)
from portfolio.portfolio_service import (
    get_holdings_list,
    create_portfolio_holding,
    update_portfolio_holding,
    delete_portfolio_holding,
    get_portfolio_summary,
    get_portfolio_performance,
)


router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


@router.get("/summary", response_model=PortfolioSummaryResponse)
def get_portfolio_summary_api(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return get_portfolio_summary(db, user_id)


@router.get("/performance", response_model=PortfolioPerformanceResponse)
def portfolio_performance(
    range: Literal["30D"] = Query("30D"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return get_portfolio_performance(db, user_id, rng=range)


@router.get("/holdings", response_model=HoldingsListResponse)
def get_portfolio_holdings(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return get_holdings_list(db, user_id)


@router.post("/holdings", response_model=HoldingUpsertResponse, status_code=201)
def create_holding(
    req: HoldingUpsertRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return create_portfolio_holding(db, user_id, req)


@router.patch("/holdings/{ticker}", response_model=HoldingUpsertResponse)
def patch_holding(
    ticker: str,
    req: HoldingUpdateRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return update_portfolio_holding(db, user_id, ticker, req)


@router.delete("/holdings/{ticker}", response_model=HoldingDeleteResponse)
def remove_holding(
    ticker: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return delete_portfolio_holding(db, user_id, ticker)