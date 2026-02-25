from sqlalchemy.orm import Session
from .buy_repository import get_buy_pattern_counts, get_total_buy_count
from .buy_schema import BuyPatternResponse, BuyPatternItem


LABEL_MAP = {
    "MOMENTUM": "모멘텀 추종형",
    "TREND_FOLLOW_UP": "추세 후속 진입형",
    "DIP_BUY": "저점매수형",
    "RECOVERY_HOPE": "회복 기대형",
    "NEWS_REACTION": "뉴스 반응형",
    "POLICY_EVENT_REACTION": "정책/공시 반응형",
    "EARNINGS_PLAY": "어닝 플레이",
    "FUNDAMENTAL_BELIEF": "펀더멘털 확신형",
    "REPORT_BASED": "리포트 기반형",
    "SECTOR_ROTATION": "섹터 로테이션형",
    "CHART_PATTERN": "차트 패턴형",
    "INDICATOR_BASED": "지표 기반형",
    "SCOUTING": "정찰병형",
    "SPLIT_BUY": "분할 매수형",
    "EXPERIMENTAL": "실험적 매수형",
    "REBALANCING": "리밸런싱",
    "AVERAGING_DOWN": "물타기형",
    "HERD_FOLLOWING": "군중추종형",
}


def calculate_buy_pattern(db: Session, user_id: int) -> BuyPatternResponse:
    rows = get_buy_pattern_counts(db, user_id)
    total_count = get_total_buy_count(db, user_id)

    patterns = [
        BuyPatternItem(
            tag=row.behavior_type,
            label=LABEL_MAP.get(row.behavior_type, row.behavior_type),
            count=row.count,
        )
        for row in rows
    ]

    return BuyPatternResponse(
        totalBuyTrades=total_count or 0,
        patterns=patterns,
    )