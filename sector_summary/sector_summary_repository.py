from sqlalchemy.orm import Session
from datetime import date
from sector_summary.sector_summary_entity import SectorSummary


def find_by_user_interest(
    db: Session,
    user_id: int,
    sector_ids: list[int],
):
    return (
        db.query(SectorSummary)
        .filter(
            SectorSummary.user_id == user_id,
            SectorSummary.sector_id.in_(sector_ids),
        )
        .order_by(SectorSummary.summary_date.desc())
        .all()
    )


def find_by_user_interest_today(
    db: Session,
    user_id: int,
    sector_ids: list[int],
    summary_date: date,
):
    return (
        db.query(SectorSummary)
        .filter(
            SectorSummary.user_id == user_id,
            SectorSummary.sector_id.in_(sector_ids),
            SectorSummary.summary_date == summary_date,
        )
        .all()
    )


def find_by_id(db: Session, summary_id: int):
    return (
        db.query(SectorSummary)
        .filter(SectorSummary.id == summary_id)
        .first()
    )


def exists_by_user_sector_date(
    db: Session,
    user_id: int,
    sector_id: int,
    summary_date: date,
) -> bool:
    return (
        db.query(SectorSummary)
        .filter(
            SectorSummary.user_id == user_id,
            SectorSummary.sector_id == sector_id,
            SectorSummary.summary_date == summary_date,
        )
        .first()
        is not None
    )


def save(db: Session, entity: SectorSummary):
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity
