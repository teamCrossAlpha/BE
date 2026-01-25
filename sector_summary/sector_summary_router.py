from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime, time, timedelta

from common.database import get_db
from common.dependencies import get_current_user_id
from interest_sector.interest_sector_repository import find_by_user
from sector_summary.sector_summary_repository import (
    find_by_user_interest_today,
    find_by_id,
)
from sector_summary.service.daily_summary import (
    run_daily_sector_summary_for_user
)

router = APIRouter(prefix="/api/sector-summaries")


def get_summary_date():
    now = datetime.now()
    if now.time() < time(9, 0):
        return date.today() - timedelta(days=1)
    return date.today()


@router.post("/run")
def run_daily_summary(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    run_daily_sector_summary_for_user(db, user_id)
    return {"message": "daily sector summary generated"}


@router.get("")
def list_summaries(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    summary_date = get_summary_date()

    interests = find_by_user(db, user_id)
    sector_ids = [i.sector_id for i in interests]

    summaries = find_by_user_interest_today(
        db, sector_ids, summary_date
    )

    return {
        "count": len(summaries),
        "summaries": [
            {
                "summaryId": s.id,
                "title": s.title,
                "preview": s.preview,
                "summaryDate": s.summary_date,
            }
            for s in summaries
        ]
    }


@router.get("/{summary_id}")
def summary_detail(
    summary_id: int,
    db: Session = Depends(get_db),
):
    s = find_by_id(db, summary_id)
    if not s:
        raise HTTPException(status_code=404)

    return {
        "id": s.id,
        "title": s.title,
        "preview": s.preview,
        "content": s.content,
        "keyPoints": s.key_points,
        "sources": s.sources,
    }
