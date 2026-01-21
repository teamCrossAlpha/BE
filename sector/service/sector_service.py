from sqlalchemy.orm import Session

from sector.sector_repository import find_all
from interest_sector.interest_sector_repository import find_by_user
from sector.service.finnhub_service import get_all_sector_return_rates


def get_sector_overview(db: Session, user_id: int):
    sectors = find_all(db)
    interest_sectors = find_by_user(db, user_id)

    favorite_sector_ids = {
        interest.sector_id for interest in interest_sectors
    }

    sector_return_rates = get_all_sector_return_rates()

    result = []
    for sector in sectors:
        result.append({
            "sectorKey": sector.sector_key,
            "sectorDisplay": sector.sector_display,
            "returnRate": sector_return_rates.get(sector.sector_key, 0.0),
            "isFavorite": sector.id in favorite_sector_ids,
        })

    return result
