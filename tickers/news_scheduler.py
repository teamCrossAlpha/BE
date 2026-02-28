import time
import datetime as dt
import json
from sqlalchemy.orm import Session
from openai import OpenAI

from common.database import SessionLocal
from common.config import settings
from tickers.ticker_news_entity import TickerNews
from tickers.tickers_entity import Ticker
from tickers.tickers_service import _alpha_vantage_get


client = OpenAI(api_key=settings.openai_api_key)


def summarize_news_batch(news_items: list[dict], ticker: str) -> list[dict]:

    if not news_items:
        return []

    prompt = f"""
다음 뉴스들을 한국어로 요약하세요.

규칙:
- title도 반드시 한국어로 번역 및 재작성
- summary는 2문장 이내
- "이 기사는", "이 보고서는", "~설명합니다" 같은 표현 절대 사용 금지
- 기사 언급 금지
- 종목 중심 문체
- 반드시 "{ticker}은(는)"으로 시작
- 간결한 투자자용 문체
- 반드시 JSON 배열만 반환

형식:
[
  {{
    "title": "한국어 제목",
    "summary": "한국어 요약"
  }}
]

뉴스 목록:
{json.dumps(news_items, ensure_ascii=False)}
"""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": "당신은 금융 뉴스 요약 전문가입니다."
            },
            {
                "role": "user",
                "content": prompt
            },
        ],
    )

    content = resp.choices[0].message.content.strip()

    try:
        return json.loads(content)
    except Exception:
        start = content.find("[")
        end = content.rfind("]")
        if start != -1 and end != -1:
            return json.loads(content[start:end+1])
        return []


def fetch_and_store_news():
    db: Session = SessionLocal()
    today = dt.date.today()

    tickers = db.query(Ticker).all()

    for i, ticker in enumerate(tickers):
        print(f"뉴스 수집 중: {ticker.ticker}")

        # 오늘 데이터 삭제
        db.query(TickerNews).filter(
            TickerNews.ticker_id == ticker.id,
            TickerNews.snapshot_date == today
        ).delete()

        data = _alpha_vantage_get({
            "function": "NEWS_SENTIMENT",
            "tickers": ticker.ticker,
            "sort": "LATEST",
            "limit": 3,
        })

        feed = data.get("feed", [])

        raw_news = [
            {
                "title": item.get("title", ""),
                "summary": item.get("summary", "")
            }
            for item in feed[:3]
        ]

        summarized_news = summarize_news_batch(raw_news, ticker.ticker)

        for original, ko in zip(feed[:3], summarized_news):

            published_at = None
            if original.get("time_published"):
                try:
                    published_at = dt.datetime.strptime(
                        original.get("time_published"),
                        "%Y%m%dT%H%M%S"
                    )
                except Exception:
                    published_at = None

            news = TickerNews(
                ticker_id=ticker.id,
                article_id=original.get("uuid") or original.get("url"),
                title=ko.get("title", ""),
                summary=ko.get("summary", ""),
                source=original.get("source"),
                url=original.get("url"),
                published_at=published_at,
                snapshot_date=today
            )

            db.add(news)

        db.commit()

        # Alpha 분당 5회 제한 대응
        if i % 5 == 4:
            time.sleep(60)

    db.close()


def run_daily_at_9():
    while True:
        now = dt.datetime.now()
        target = now.replace(hour=9, minute=0, second=0, microsecond=0)

        if now >= target:
            target += dt.timedelta(days=1)

        wait_seconds = (target - now).total_seconds()
        time.sleep(wait_seconds)

        fetch_and_store_news()