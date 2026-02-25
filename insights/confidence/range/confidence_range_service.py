from sqlalchemy.orm import Session
from .confidence_range_repository import get_confidence_range_stats
from .confidence_range_schema import (
    ConfidenceRangeResponse,
    ConfidenceZone,
    BestZoneSummary,
)


def calculate_confidence_range(db: Session, user_id: int):
    rows = get_confidence_range_stats(db, user_id)

    zones = []
    best_zone = None
    total_trades = 0

    for row in rows:
        total_trades += row.count

        weighted_return = (
            (row.total_pnl / row.total_invested) * 100
            if row.total_invested else 0
        )

        win_rate = (row.wins / row.count) * 100 if row.count else 0

        zone = ConfidenceZone(
            rangeLabel=row.range_label,
            tradeCount=row.count,
            averageReturn=round(weighted_return, 2),
            winRate=round(win_rate, 2),
        )

        zones.append(zone)

        if row.count >= 2:
            if not best_zone or weighted_return > best_zone["return"]:
                best_zone = {
                    "range": row.range_label,
                    "return": weighted_return,
                    "win_rate": win_rate,
                }

    if best_zone:
        summary = BestZoneSummary(
            bestRange=best_zone["range"],
            averageReturn=round(best_zone["return"], 2),
            winRate=round(best_zone["win_rate"], 2),
            message=f"확신 {best_zone['range']} 구간이 가장 잘 맞아요. "
                    f"평균 {round(best_zone['return'],2)}% 수익, "
                    f"승률 {round(best_zone['win_rate'],2)}%를 기록했어요.",
        )
    else:
        summary = BestZoneSummary(
            bestRange="N/A",
            averageReturn=0,
            winRate=0,
            message="아직 충분한 데이터가 없어요.",
        )

    return ConfidenceRangeResponse(
        totalCompletedTrades=total_trades,
        zones=zones,
        bestZone=summary,
    )