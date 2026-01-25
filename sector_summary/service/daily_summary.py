from sqlalchemy.orm import Session
from common.date_utils import get_summary_date
from interest_sector.interest_sector_repository import find_by_user
from sector.sector_repository import find_by_ids
from sector_summary.service.news_collector import fetch_sector_news
from sector_summary.service.gpt_summarizer import summarize_sector
from sector_summary.sector_summary_entity import SectorSummary
from sector_summary.sector_summary_repository import (
    save, exists_by_user_sector_date
)

def run_daily_sector_summary_for_user(
    db: Session,
    user_id: int
):
    summary_date = get_summary_date()

    interests = find_by_user(db, user_id)
    if not interests:
        return

    sector_ids = [i.sector_id for i in interests]
    sectors = find_by_ids(db, sector_ids)

    for sector in sectors:
        # 🔥 중복 방지
        if exists_by_user_sector_date(
            db, user_id, sector.id, summary_date
        ):
            continue

        articles = fetch_sector_news(sector.sector_key)
        if not articles:
            continue

        result = summarize_sector(
            sector.sector_key,
            sector.sector_display,
            articles
        )

        entity = SectorSummary(
            user_id=user_id,
            sector_id=sector.id,
            summary_date=summary_date,
            title=result["title"],
            preview=result["preview"],
            content=result["content"],
            key_points=result["key_points"],
            sources=result["sources"],
        )

        save(db, entity)
