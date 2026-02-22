from sqlalchemy.orm import Session
from sqlalchemy import func

from trades.trades_entity import Asset, Holding, Trade, TradeResult


def get_or_create_asset(db: Session, ticker: str) -> Asset:
    t = ticker.upper().strip()
    asset = db.query(Asset).filter(Asset.ticker == t).first()
    if not asset:
        asset = Asset(ticker=t, name=t)  # name 임시
        db.add(asset)
        db.flush()
    return asset


def get_holding(db: Session, user_id: int, ticker: str) -> Holding | None:
    t = ticker.upper().strip()
    return db.query(Holding).filter(Holding.user_id == user_id, Holding.ticker == t).first()


def upsert_holding(db: Session, user_id: int, ticker: str, quantity: int, avg_price):
    t = ticker.upper().strip()
    h = get_holding(db, user_id, t)
    if not h:
        h = Holding(user_id=user_id, ticker=t, quantity=quantity, average_price=avg_price)
        db.add(h)
        db.flush()
        return h

    h.quantity = quantity
    h.average_price = avg_price
    db.flush()
    return h


def create_trade(db: Session, trade: Trade) -> Trade:
    db.add(trade)
    db.flush()
    return trade


def create_trade_result(db: Session, tr: TradeResult) -> TradeResult:
    db.add(tr)
    db.flush()
    return tr


def list_trades(db: Session, user_id: int, sort_field: str | None, sort_order: str | None):
    q = db.query(Trade).filter(Trade.user_id == user_id)

    if sort_field == "tradeDate":
        col = Trade.trade_date
    elif sort_field == "confidence":
        col = Trade.confidence
    else:
        col = Trade.id

    is_asc = (sort_order or "").lower() == "asc"
    return q.order_by(col.asc() if is_asc else col.desc()).all()


def get_trade(db: Session, user_id: int, trade_id: int) -> Trade | None:
    return db.query(Trade).filter(Trade.user_id == user_id, Trade.id == trade_id).first()


def get_summary(db: Session, user_id: int):
    # 전체 거래 수
    total_trades = db.query(func.count(Trade.id)).filter(Trade.user_id == user_id).scalar() or 0

    # 평균 confidence (null 제외)
    avg_conf = db.query(func.avg(Trade.confidence)).filter(Trade.user_id == user_id).scalar()
    avg_conf = int(round(float(avg_conf))) if avg_conf is not None else 0

    # 승률/최고수익률: "전량청산(EXIT)인 SELL"만 포지션 종료로 간주
    exit_sell_q = (
        db.query(TradeResult)
        .join(Trade, Trade.id == TradeResult.trade_id)
        .filter(
            Trade.user_id == user_id,
            Trade.trade_type == "SELL",
            Trade.position_action == "EXIT",
        )
    )

    exit_count = exit_sell_q.count()

    win_count = exit_sell_q.filter(
        TradeResult.pnl_rate.isnot(None),
        TradeResult.pnl_rate > 0
    ).count()

    win_rate = (win_count / exit_count) if exit_count > 0 else 0

    best_return = exit_sell_q.with_entities(func.max(TradeResult.pnl_rate)).scalar()
    best_return = float(best_return) if best_return is not None else 0

    return total_trades, win_rate, avg_conf, best_return
