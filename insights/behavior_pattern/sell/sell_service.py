from sqlalchemy.orm import Session
from .sell_repository import get_completed_sell_trades
from .sell_schema import SellPatternResponse, SellPatternItem

LABEL_MAP = {
    # 1. 이익실현형
    "TARGET_HIT": "목표가 달성형",
    "QUICK_PROFIT": "짧은 차익형",

    # 2. 손절형
    "LOSS_LIMIT": "손실 제한형",
    "DOWNSIDE_DEFENSE": "추가 하락 방어형",

    # 3. 추세전환형
    "TECH_SIGNAL": "기술적 신호형",
    "FUNDAMENTAL_CHANGE": "펀더멘털 변화형",

    # 4. 리스크 회피형
    "VOLATILITY_RESPONSE": "변동성 대응형",
    "PORTFOLIO_ADJUSTMENT": "포트폴리오 조정형",

    # 5. 기회비용형
    "BETTER_OPPORTUNITY": "더 나은 기회 발견형",

    # 6. 자금 관리형
    "EMERGENCY_LIQUIDITY": "긴급 유동성 확보형",
    "PLANNED_LIQUIDATION": "계획적 청산형",

    # 7. 감정반응형
    "FEAR_SELL": "공포 매도형",
    "SELF_BLAME_SELL": "자책성 매도형",
}


def calculate_sell_pattern(db: Session, user_id: int) -> SellPatternResponse:
    sell_trades = get_completed_sell_trades(db, user_id)

    stats = {}

    for sell in sell_trades:
        tag = sell.behavior_type
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
            SellPatternItem(
                tag=tag,
                label=LABEL_MAP.get(tag, tag),
                count=count,
                winRate=round(win_rate, 2),
                averageReturn=round(avg_return * 100, 2),
            )
        )

    return SellPatternResponse(
        totalSellTrades=total,
        patterns=patterns,
    )