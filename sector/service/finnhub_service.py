import requests
from common.config import settings

FINNHUB_URL = "https://finnhub.io/api/v1/quote"

SECTOR_ETF_MAP = {
    "technology": "XLK",
    "energy": "XLE",
    "healthcare": "XLV",
    "financials": "XLF",
    "industrials": "XLI",
}


def get_all_sector_return_rates() -> dict[str, float]:
    if not settings.finnhub_api_key:
        return {}

    result: dict[str, float] = {}

    for sector_key, etf_symbol in SECTOR_ETF_MAP.items():
        response = requests.get(
            FINNHUB_URL,
            params={
                "symbol": etf_symbol,
                "token": settings.finnhub_api_key,
            },
            timeout=5,
        )

        response.raise_for_status()
        data = response.json()

        current = data.get("c")   # 현재가
        prev_close = data.get("pc")  # 전일 종가

        if current and prev_close and prev_close != 0:
            rate = (current - prev_close) / prev_close * 100
            result[sector_key] = round(rate, 2)
        else:
            result[sector_key] = 0.0

    return result
