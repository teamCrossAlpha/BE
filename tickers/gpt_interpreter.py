import json
import os
from typing import Optional, Literal

from openai import OpenAI

from common.config import settings
from tickers.tickers_schema import TechnicalSnapshot, ExplainResult


SYSTEM_PROMPT = """
당신은 초보 개인 투자자를 위한 기술적 지표 해설 전문가입니다.

반드시 지켜야 할 것:
- 모든 결과는 한국어로 작성합니다.
- 매수/매도, 종목 추천 등 직접적인 투자 조언을 하지 않습니다.
- 미래 가격을 단정적으로 예측하지 않습니다.
- 입력 스냅샷(JSON)에 포함된 정보만 근거로 사용합니다.
- 초보자도 이해할 수 있게, 전문 용어는 필요 시 ( )로 짧게 풀어 씁니다.

출력 규칙:
- 반드시 JSON 객체만 출력합니다. (설명문/코드블록/추가 텍스트 금지)
- JSON 스키마:
  {
    "signals": [
      {"id": "...", "title": "...", "description": "...", "strength": "LOW|MEDIUM|HIGH"}
    ],
    "summaryText": "..."
  }
- signals는 2~4개로 작성합니다.
""".strip()

Purpose = Literal["tech", "news"]


def _get_openai_api_key(purpose: Purpose = "tech") -> str:
    """
    목적별 키 선택:
    - tech: OPENAI_TECH_API_KEY 우선, 없으면 OPENAI_API_KEY 폴백
    - news: OPENAI_API_KEY

    우선순위:
    1) settings 필드
    2) 환경변수(os.getenv)
    """
    if purpose == "tech":
        # 1) tech 전용 키 우선
        tech_key: Optional[str] = getattr(settings, "openai_tech_api_key", None)
        if tech_key:
            return tech_key

        env_tech_key = os.getenv("OPENAI_TECH_API_KEY")
        if env_tech_key:
            return env_tech_key

        # 2) 폴백: 기존 공용 키
        fallback = getattr(settings, "openai_api_key", None) or os.getenv("OPENAI_API_KEY")
        if fallback:
            return fallback

    if purpose == "news":
        # news는 기존 공용 키 사용
        news_key: Optional[str] = getattr(settings, "openai_api_key", None)
        if news_key:
            return news_key

        env_news_key = os.getenv("OPENAI_API_KEY")
        if env_news_key:
            return env_news_key

    raise RuntimeError(
        "OpenAI API Key가 없습니다. "
        "OPENAI_TECH_API_KEY 또는 OPENAI_API_KEY를 .env에 설정하세요."
    )


def _get_openai_client(purpose: Purpose = "tech") -> OpenAI:
    return OpenAI(api_key=_get_openai_api_key(purpose))


def explain_snapshot_with_openai(
    snapshot: TechnicalSnapshot,
    purpose: Purpose = "tech",
) -> ExplainResult:
    """
    TechnicalSnapshot 기반으로 signals/summaryText를 생성합니다.
    - purpose 기본값을 tech로 둬서 tickers 쪽은 기존 호출부 수정 없이 그대로 돌아가게 함.
    """
    client = _get_openai_client(purpose)

    user_prompt = f"""
아래는 기술적 지표 스냅샷(JSON)입니다.
이 정보를 바탕으로 signals와 summaryText를 작성하세요.

주의:
- 투자 조언/추천/예측 금지
- JSON 객체만 출력

스냅샷(JSON):
{snapshot.model_dump_json(ensure_ascii=False, indent=2)}
""".strip()

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=600,
    )

    content = resp.choices[0].message.content or "{}"

    # JSON 파싱 안정화
    try:
        data = json.loads(content)
    except Exception:
        start = content.find("{")
        end = content.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError(f"OpenAI JSON 파싱 실패: {content}")
        data = json.loads(content[start : end + 1])

    return ExplainResult.model_validate(data)
