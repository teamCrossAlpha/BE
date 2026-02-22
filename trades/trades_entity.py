from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Date,
    Numeric,
    DateTime,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    func,
    JSON
)
from sqlalchemy.orm import relationship

from common.database import Base


# BUY 행동 태그
BUY_BEHAVIOR_TYPES = (
    # 1. 추세추종형
    "MOMENTUM",
    "TREND_FOLLOW_UP",
    # 2. 역추세형
    "DIP_BUY",
    "RECOVERY_HOPE",
    # 3. 이벤트 반응형
    "NEWS_REACTION",
    "POLICY_EVENT_REACTION",
    "EARNINGS_PLAY",
    # 4. 가치신념형
    "FUNDAMENTAL_BELIEF",
    "REPORT_BASED",
    "SECTOR_ROTATION",
    # 5. 기술적 분석형
    "CHART_PATTERN",
    "INDICATOR_BASED",
    # 6. 전략적 매수형
    "SCOUTING",
    "SPLIT_BUY",
    "EXPERIMENTAL",
    # 7. 복구형
    "REBALANCING",
    "AVERAGING_DOWN",
    # 8. FOMO형
    "HERD_FOLLOWING",
)

# SELL 행동 태그
SELL_BEHAVIOR_TYPES = (
    # 1. 이익실현형
    "TARGET_HIT",
    "QUICK_PROFIT",
    # 2. 손절형
    "LOSS_LIMIT",
    "DOWNSIDE_DEFENSE",
    # 3. 추세전환형
    "TECH_SIGNAL",
    "FUNDAMENTAL_CHANGE",
    # 4. 리스크 회피형
    "VOLATILITY_RESPONSE",
    "PORTFOLIO_ADJUSTMENT",
    # 5. 기회비용형
    "BETTER_OPPORTUNITY",
    # 6. 자금 관리형
    "EMERGENCY_LIQUIDITY",
    "PLANNED_LIQUIDATION",
    # 7. 감정반응형
    "FEAR_SELL",
    "SELF_BLAME_SELL",
)

# DB CHECK는 전체 집합만 허용 (BUY/SELL 분기 검증은 서비스에서)
BEHAVIOR_TYPES = BUY_BEHAVIOR_TYPES + SELL_BEHAVIOR_TYPES

POSITION_ACTIONS = ("ENTRY", "ADD", "PARTIAL_EXIT", "EXIT")


class Asset(Base):
    __tablename__ = "assets"

    ticker = Column(String(16), primary_key=True)
    name = Column(String(255), nullable=False)
    currency = Column(String(8), nullable=True)
    market_cap = Column(Numeric(20, 2), nullable=True)
    meta_updated_at = Column(DateTime(timezone=True), nullable=False,server_default=func.now(),
    onupdate=func.now(),) # 데이터 마지막 갱신 시각
    sector = Column(String(100), nullable=True)



class Holding(Base):
    __tablename__ = "holdings"
    __table_args__ = (
        UniqueConstraint("user_id", "ticker", name="uq_holdings_user_ticker"),
        CheckConstraint("quantity >= 0", name="chk_holdings_quantity"),
        CheckConstraint(
            "average_price IS NULL OR average_price >= 0",
            name="chk_holdings_avg_price",
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    user_id = Column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ticker = Column(String(16), ForeignKey("assets.ticker"), nullable=False)

    quantity = Column(Integer, nullable=False)
    average_price = Column(Numeric(18, 4), nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Trade(Base):
    __tablename__ = "trades"
    __table_args__ = (
        CheckConstraint("trade_type IN ('BUY','SELL')", name="chk_trade_type"),
        CheckConstraint("price > 0", name="chk_trade_price"),
        CheckConstraint("quantity > 0", name="chk_trade_quantity"),
        CheckConstraint(
            "confidence IS NULL OR (confidence BETWEEN 0 AND 100)",
            name="chk_trade_confidence",
        ),
        CheckConstraint(
            "behavior_type IN (" + ",".join(f"'{b}'" for b in BEHAVIOR_TYPES) + ")",
            name="chk_trade_behavior_type",
        ),
        CheckConstraint(
            "position_action IN ('ENTRY','ADD','PARTIAL_EXIT','EXIT')",
            name="chk_trade_position_action",
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    ticker = Column(String(16), ForeignKey("assets.ticker"), nullable=False)

    trade_type = Column(String(10), nullable=False)  # BUY/SELL
    trade_date = Column(Date, nullable=False)

    price = Column(Numeric(18, 4), nullable=False)
    quantity = Column(Integer, nullable=False)

    confidence = Column(Integer, nullable=True)
    behavior_type = Column(String(50), nullable=False)
    memo = Column(String(2000), nullable=True)

    # 이벤트 라벨 (진입/부분 매수/부분 매도/전량 매도)
    position_action = Column(String(20), nullable=False)  # ENTRY/ADD/PARTIAL_EXIT/EXIT

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    result = relationship(
        "TradeResult",
        uselist=False,
        back_populates="trade",
        cascade="all, delete-orphan",
    )


class TradeResult(Base):
    __tablename__ = "trade_results"
    __table_args__ = (
        CheckConstraint("pnl_status IN ('OPEN','CLOSED')", name="chk_pnl_status"),
    )

    trade_id = Column(
        BigInteger, ForeignKey("trades.id", ondelete="CASCADE"), primary_key=True
    )

    pnl_status = Column(String(10), nullable=False, default="OPEN")  # OPEN/CLOSED
    pnl_amount = Column(Numeric(18, 4), nullable=True)
    pnl_rate = Column(Numeric(10, 6), nullable=True)
    closed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    trade = relationship("Trade", back_populates="result")


class TradeMarketSnapshot(Base):
    __tablename__ = "trade_market_snapshots"
    __table_args__ = (
        UniqueConstraint("trade_id", "type", "range", name="uq_trade_snapshot"),
        CheckConstraint("type IN ('quant','qual')", name="chk_snapshot_type"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    trade_id = Column(
        BigInteger, ForeignKey("trades.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # quant / qual
    type = Column(String(10), nullable=False)

    # quant만 사용: '3M'|'6M'|'1Y' / qual은 None
    range = Column(String(10), nullable=True)

    captured_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # 실제 payload 저장 (정량/정성 결과 JSON)
    data = Column(JSON, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )