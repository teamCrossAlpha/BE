from sqlalchemy.orm import Session

from .performance_repository import get_sell_trades_for_performance
from .performance_schema import (
    PerformanceScoreResponse,
    WinRateDTO,
    AvgReturnDTO,
    BadPatternDTO,
    ConvictionDTO,
    TextBonusDTO,
)

BAD_PATTERNS = {"HERD_FOLLOWING", "FEAR_SELL", "SELF_BLAME_SELL"}


def _clamp(value, min_v, max_v):
    return max(min_v, min(value, max_v))


def calculate_performance_score(db: Session, user_id: int) -> PerformanceScoreResponse:

    # 🔹 전체 종료된 SELL 거래를 오래된 순으로 가져옴
    all_trades = get_sell_trades_for_performance(db, user_id)

    total_count = len(all_trades)

    # 🔹 10단위로 사용할 개수 계산
    usable_count = (total_count // 10) * 10

    # 🔹 10건 미만이면 안내 메시지 반환
    if usable_count == 0:
        return PerformanceScoreResponse(
            totalScore=0,
            winRate=WinRateDTO(score=0, wins=0, total=total_count, ratio=0),
            averageReturn=AvgReturnDTO(score=0, averageRate=0),
            badPattern=BadPatternDTO(score=0, badCount=0, ratio=0),
            conviction=ConvictionDTO(
                score=0,
                rawScore=0,
                lowConfidenceWins=0,
                message="퍼포먼스 점수는 10건 이상의 매도 거래가 필요합니다.",
            ),
            textBonus=TextBonusDTO(score=0, writeRatio=0),
        )

    # 🔹 가장 오래된 usable_count개만 사용
    trades = all_trades[:usable_count]
    total = len(trades)

    # ---------------- 승률 ----------------
    wins = sum(1 for t in trades if float(t.result.pnl_rate or 0) > 0)
    win_ratio = wins / total
    win_score = win_ratio * 20

    # ---------------- 평균 수익률 ----------------
    avg_rate = sum(float(t.result.pnl_rate or 0) for t in trades) / total
    normalized = ((avg_rate + 0.15) / 0.30) * 30
    avg_score = _clamp(normalized, 0, 30)

    # ---------------- 나쁜 패턴 ----------------
    bad_count = sum(1 for t in trades if t.behavior_type in BAD_PATTERNS)
    bad_ratio = bad_count / total
    bad_score = 20 - (bad_ratio * 20)

    # ---------------- Conviction ----------------
    raw_score = 0
    low_conf_win = 0

    for t in trades:
        rate = float(t.result.pnl_rate or 0)
        conf = (t.confidence or 0) / 10  # 0~100 → 0~10 스케일 변환

        if conf >= 8:
            raw_score += 1.5 if rate > 0 else -1.5
        elif conf >= 5:
            raw_score += 1.0 if rate > 0 else -1.0
        else:
            if rate > 0:
                low_conf_win += 1
            else:
                raw_score -= 0.7

    max_score = total * 1.5
    conviction_score = max(0, (raw_score / max_score) * 30)

    message = None
    if 1 <= low_conf_win <= 2:
        message = "복기해볼 만한 거래가 있어요"
    elif 3 <= low_conf_win <= 5:
        message = f"확신 없이 수익난 거래가 {low_conf_win}건, 패턴을 찾아보세요"
    elif low_conf_win >= 6:
        message = "수익의 상당수가 저확신 거래에서 나오고 있어요. 시장 환경이 바뀌면 결과가 달라질 수 있어요"

    # ---------------- 텍스트 보너스 ----------------
    memo_count = sum(1 for t in trades if t.memo and t.memo.strip())
    write_ratio = memo_count / total
    text_bonus = write_ratio * 5

    # ---------------- 총점 ----------------
    total_score = win_score + avg_score + bad_score + conviction_score + text_bonus

    return PerformanceScoreResponse(
        totalScore=round(total_score, 2),
        winRate=WinRateDTO(
            score=round(win_score, 2),
            wins=wins,
            total=total,
            ratio=win_ratio,
        ),
        averageReturn=AvgReturnDTO(
            score=round(avg_score, 2),
            averageRate=round(avg_rate, 4),
        ),
        badPattern=BadPatternDTO(
            score=round(bad_score, 2),
            badCount=bad_count,
            ratio=bad_ratio,
        ),
        conviction=ConvictionDTO(
            score=round(conviction_score, 2),
            rawScore=round(raw_score, 2),
            lowConfidenceWins=low_conf_win,
            message=message,
        ),
        textBonus=TextBonusDTO(
            score=round(text_bonus, 2),
            writeRatio=write_ratio,
        ),
    )