import requests
import datetime as dt
from common.config import settings

ALPHA_URL = "https://www.alphavantage.co/query"


def fetch_sector_news(topic: str) -> list[dict]:
    time_from = (
        dt.datetime.utcnow() - dt.timedelta(days=7)
    ).strftime("%Y%m%dT%H%M")

    res = requests.get(
        ALPHA_URL,
        params={
            "function": "NEWS_SENTIMENT",
            "topics": topic,
            "time_from": time_from,
            "limit": 8,
            "apikey": settings.alpha_vantage_api_key,
        },
        timeout=10,
    )

    res.raise_for_status()
    return res.json().get("feed", [])
