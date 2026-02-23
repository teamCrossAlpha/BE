from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

import yfinance as yf


@dataclass
class QuoteFields:
    price: Decimal
    change: Optional[Decimal]
    change_rate: Optional[Decimal]


def fetch_quote_fields(ticker: str) -> QuoteFields:
    """
    yfinance로 현재가/전일대비(change)/등락률(change_rate) 추출.
    - change = price - prev_close
    - change_rate = change / prev_close   (예: -0.0505)
    """
    t = ticker.upper().strip()
    yt = yf.Ticker(t)

    # 1) info에 값이 있으면 우선 사용
    price = None
    prev_close = None

    try:
        info = yt.fast_info
        # fast_info는 키가 환경마다 다를 수 있어 방어적으로 접근
        price = getattr(info, "last_price", None) or getattr(info, "lastPrice", None) or getattr(info, "last", None)
        prev_close = getattr(info, "previous_close", None) or getattr(info, "previousClose", None)
    except Exception:
        pass

    # 2) fast_info 실패 시 history로 fallback
    if price is None or prev_close is None:
        hist = yt.history(period="5d", interval="1d")
        if hist is None or hist.empty:
            raise ValueError(f"yfinance history is empty for ticker={t}")

        # 최근 2거래일 확보
        closes = hist["Close"].dropna().tolist()
        if len(closes) == 1:
            last_price = float(closes[-1])
            prev = None
        else:
            last_price = float(closes[-1])
            prev = float(closes[-2])

        price = price if price is not None else last_price
        prev_close = prev_close if prev_close is not None else prev

    # price는 필수
    if price is None:
        raise ValueError(f"Failed to fetch price for ticker={t}")

    price_d = Decimal(str(price))

    change_d: Optional[Decimal] = None
    change_rate_d: Optional[Decimal] = None

    if prev_close is not None:
        prev_d = Decimal(str(prev_close))
        if prev_d != 0:
            change_d = price_d - prev_d
            change_rate_d = change_d / prev_d

    return QuoteFields(
        price=price_d,
        change=change_d,
        change_rate=change_rate_d,
    )