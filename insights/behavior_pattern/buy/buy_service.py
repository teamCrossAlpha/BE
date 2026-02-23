from sqlalchemy.orm import Session
from .buy_repository import get_completed_sell_trades, find_buy_for_sell
from .buy_schema import BuyPatternResponse, BuyPatternItem

LABEL_MAP = {
    # 1. 추세추종형
    "MOMENTUM": "모멘텀 추종형",
    "TREND_FOLLOW_UP": "추세 후속 진입형",

    # 2. 역추세형
    "DIP_BUY": "저점매수형",
    "RECOVERY_HOPE": "회복 기대형",

    # 3. 이벤트 반응형
    "NEWS_REACTION": "뉴스 반응형",
    "POLICY_EVENT_REACTION": "정책/공시 반응형",
    "EARNINGS_PLAY": "어닝 플레이",

    # 4. 가치신념형
    "FUNDAMENTAL_BELIEF": "펀더멘털 확신형",
    "REPORT_BASED": "리포트 기반형",
    "SECTOR_ROTATION": "섹터 로테이션형",

    # 5. 기술적 분석형
    "CHART_PATTERN": "차트 패턴형",
    "INDICATOR_BASED": "지표 기반형",

    # 6. 전략적 매수형
    "SCOUTING": "정찰병형",
    "SPLIT_BUY": "분할 매수형",
    "EXPERIMENTAL": "실험적 매수형",

    # 7. 복구형
    "REBALANCING": "리밸런싱",
    "AVERAGING_DOWN": "물타기형",

    # 8. FOMO형
    "HERD_FOLLOWING": "군중추종형",
}


def calculate_buy_pattern(db: Session, user_id: int) -> BuyPatternResponse:
    sell_trades = get_completed_sell_trades(db, user_id)

    stats = {}

    for sell in sell_trades:
        buy = find_buy_for_sell(db, sell)
        if not buy:
            continue

        tag = buy.behavior_type
        pnl = float(sell.result.pnl_rate)

        if tag not in stats:
            stats[tag] = {
                "count": 0,
                "wins": 0,
                "total_return": 0.0,
            }

        stats[tag]["count"] += 1
        stats[tag]["total_return"] += pnl
        if pnl > 0:
            stats[tag]["wins"] += 1

    patterns = []
    total = 0

    for tag, data in stats.items():
        count = data["count"]
        total += count
        win_rate = (data["wins"] / count) * 100 if count else 0
        avg_return = data["total_return"] / count if count else 0

        patterns.append(
            BuyPatternItem(
                tag=tag,
                label=LABEL_MAP.get(tag, tag),
                count=count,
                winRate=round(win_rate, 2),
                averageReturn=round(avg_return * 100, 2),
            )
        )

    return BuyPatternResponse(
        totalCompletedTrades=total,
        patterns=patterns,
    )