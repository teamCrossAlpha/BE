from sqlalchemy.orm import Session
from openai import OpenAI
import json

from common.config import settings

from trades.trades_entity import Trade
from insights.action_plan.action_plan_entity import ActionPlan
from insights.action_plan.action_plan_repository import (
    get_latest_action_plan,
    create_action_plan
)

client = OpenAI(api_key=settings.openai_api_key)


SYSTEM_PROMPT = """
당신은 CrossAlpha의 트레이딩 코치입니다.

사용자의 최근 매매일지 10건을 분석하여 
행동 패턴을 우선순위 기반으로 분석하고
실질적인 액션 플랜을 제공합니다.

---

## 핵심 분석 전략

반드시 아래 순서대로 판단하세요:

### 1️. 부정 패턴 존재 여부 판단

다음 중 하나라도 해당하면 "부정 패턴 존재"로 판단:
- 반복된 위험 행동 (2회 이상)
- 손실로 이어진 패턴
- 감정 기반 매매 (FOMO, 공포매도 등)
- 확신도와 결과의 불일치

⚠️ 중요:
- 최근 3건 내에서 발생한 부정 패턴은 
  단 1~2회라도 강한 신호로 간주하세요

👉 이 경우:
→ 부정 패턴을 최우선으로 분석하세요
→ 긍정 행동은 보조로 간단히 언급

---

### 2️. 부정 패턴이 뚜렷하지 않은 경우

👉 이 경우:
→ 긍정 행동을 중심으로 분석하세요
→ 잘한 전략을 강조하고 유지하도록 피드백하세요

---

## 3. 공통 분석 규칙

- 반드시 최소 2개 이상의 거래를 근거로 사용하세요
- 하나의 거래만 보고 판단하지 마세요
- 거래 흐름 전체를 고려하세요

---

### 3-1. 시간 가중치 규칙 (매우 중요)

- 최근 거래일수록 더 높은 중요도로 판단하세요
- 특히 최근 3건의 거래는 전체 판단에 가장 큰 영향을 줍니다
- 오래된 거래보다 최근 거래에서 반복되는 패턴을 우선적으로 해석하세요

👉 우선순위 기준:
1. 최근 3건에서 반복되는 패턴 → 최우선
2. 최근 5건에서 나타나는 흐름 → 중요
3. 전체 10건에서의 장기 패턴 → 보조 참고

- 과거에 존재했던 패턴이라도 최근에 개선되었다면 "개선된 행동"으로 평가하세요
- 반대로 과거에는 없던 문제라도 최근에 발생했다면 "새로운 위험 패턴"으로 판단하세요

---

## 제목 생성 규칙 

제목은 반드시:

- "행동 패턴 + 평가 + 개선 방향" 구조
- 구체적인 행동 포함 (FOMO, 물타기, 공포매도 등)
- 피드백 포함 ("주의하세요", "개선하세요", "유지하세요", "명확히 하세요")

❌ 금지:
- "매수 전략 개선"
- "매도 전략 강화"
- 단순 요약형 제목

---

## summary 작성 규칙

### 부정 패턴이 있는 경우
- 2~3문장
- 반드시 포함:
  1. 반복 문제 패턴
  2. 왜 위험한지
  3. 개선 방향

- 추가:
  - 긍정 행동이 있다면 마지막 문장에 짧게 언급

---

### 부정 패턴이 없는 경우
- 2~3문장
- 반드시 포함:
  1. 잘한 행동 패턴
  2. 왜 좋은지 (근거)
  3. 유지 권장 ("이 전략은 유지하세요")

---

## 출력 형식

{
  "buy_action_plan": {
    "title": "",
    "summary": "",
    "referenced_trade_ids": []
  },
  "sell_action_plan": {:wq
  
    "title": "",
    "summary": "",
    "referenced_trade_ids": []
  }
}
"""

# =========================
# USER PROMPT
# =========================
def _build_user_prompt(trades_json):
    return f"""
아래는 사용자의 최근 매매일지 10건입니다.

반드시 거래 흐름 전체를 보고
반복 패턴 + 위험 행동 + 확신도 불일치를 중심으로 분석하세요.

{json.dumps(trades_json, ensure_ascii=False)}
"""


# =========================
# 변환
# =========================
def _convert_to_gpt_format(trades):
    return {
        "trades": [
            {
                "id": t.id,
                "type": "buy" if t.trade_type == "BUY" else "sell",
                "ticker": t.ticker,
                "date": str(t.trade_date),
                "price": float(t.price),
                "quantity": t.quantity,
                "reason": t.memo or "",
                "conviction": t.confidence or 0,
                "behavior_tag": t.behavior_type
            }
            for t in trades
        ]
    }


# =========================
# GPT 호출
# =========================
def _call_gpt(trades_json):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(trades_json)}
        ],
    )

    content = response.choices[0].message.content.strip()
    return json.loads(content)


# =========================
# 최근 거래
# =========================
def _get_recent_trades(db: Session, user_id: int):
    return (
        db.query(Trade)
        .filter(Trade.user_id == user_id)
        .order_by(Trade.trade_date.desc())
        .limit(10)
        .all()
    )


# =========================
# 생성
# =========================
def _generate_and_save(db: Session, user_id: int):
    trades = _get_recent_trades(db, user_id)

    if len(trades) < 10:
        return None

    latest_trade = trades[0]
    last_plan = get_latest_action_plan(db, user_id)

    if last_plan and last_plan.last_trade_id == latest_trade.id:
        return last_plan

    gpt_result = _call_gpt(_convert_to_gpt_format(trades))

    action_plan = ActionPlan(
        user_id=user_id,
        last_trade_id=latest_trade.id,

        buy_title=gpt_result["buy_action_plan"]["title"],
        buy_summary=gpt_result["buy_action_plan"]["summary"],
        buy_referenced_trade_ids=gpt_result["buy_action_plan"]["referenced_trade_ids"],

        sell_title=gpt_result["sell_action_plan"]["title"],
        sell_summary=gpt_result["sell_action_plan"]["summary"],
        sell_referenced_trade_ids=gpt_result["sell_action_plan"]["referenced_trade_ids"],
    )

    return create_action_plan(db, action_plan)


# =========================
# GET (자동 생성 포함)
# =========================
def get_latest_action_plan_service(db: Session, user_id: int):

    plan = _generate_and_save(db, user_id)

    if not plan:
        raise Exception("데이터 부족")

    return {
        "buy_action_plan": {
            "title": plan.buy_title,
            "summary": plan.buy_summary,
            "referenced_trade_ids": plan.buy_referenced_trade_ids
        },
        "sell_action_plan": {
            "title": plan.sell_title,
            "summary": plan.sell_summary,
            "referenced_trade_ids": plan.sell_referenced_trade_ids
        },
        "created_at": plan.created_at.isoformat()
    }