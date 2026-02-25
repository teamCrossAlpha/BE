from sqlalchemy.orm import Session
from .sell_repository import get_sell_pattern_stats
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


def calculate_sell_pattern(db: Session, user_id: int):
    rows = get_sell_pattern_stats(db, user_id)

    patterns = []

    for row in rows:
        win_rate = (row.wins / row.count) * 100 if row.count else 0

        weighted_return = (
            (row.total_pnl / row.total_invested) * 100
            if row.total_invested else 0
        )

        patterns.append(
            SellPatternItem(
                tag=row.behavior_type,
                label=LABEL_MAP.get(row.behavior_type, row.behavior_type),
                count=row.count,
                winRate=round(win_rate, 2),
                averageReturn=round(weighted_return, 2),
            )
        )

    return SellPatternResponse(
        totalCompletedTrades=sum(p.count for p in patterns),
        patterns=patterns,
    )