from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from common.database import SessionLocal
from portfolio.portfolio_snapshot_service import run_daily_portfolio_snapshot_for_user

from sector_summary.service.daily_summary import (
    run_daily_sector_summary_for_user
)
from user.user_entity import User

import time
from datetime import datetime
from trades.trades_entity import Asset
from tickers.tickers_service import (
    refresh_asset_overview_if_needed,
)

MAX_ASSETS_PER_RUN = 10  # 한 번 실행에서 갱신할 최대 종목 수(무료 API 호출 횟수 제한으로 인해 임시 적용)

def start_scheduler(app):
    scheduler = BackgroundScheduler(timezone="Asia/Seoul")

    def daily_summary_job():
        db: Session = SessionLocal()
        try:

            user_ids = (
                db.query(User.id)
                .all()
            )

            user_ids = [user_id for (user_id,) in user_ids]

            for user_id in user_ids:
                run_daily_sector_summary_for_user(db, user_id)

        finally:
            db.close()

    scheduler.add_job(
        daily_summary_job,
        trigger="cron",
        hour=9,
        minute=0,
        id="daily_sector_summary",
        replace_existing=True,
    )

    def daily_asset_meta_job():
        db: Session = SessionLocal()
        try:
            assets = (
                db.query(Asset)
                .order_by(Asset.meta_updated_at.is_(None).desc(), Asset.meta_updated_at.asc())
                .limit(MAX_ASSETS_PER_RUN)
                .all()
            )

            print(f"[daily_asset_meta_job] 대상 종목 수: {len(assets)}")

            for asset in assets:
                try:
                    print(f"[daily_asset_meta_job] 시작: {asset.ticker}, meta_updated_at={asset.meta_updated_at}")
                    refresh_asset_overview_if_needed(db, asset, ttl_hours=24)
                    print(f"[daily_asset_meta_job] 완료: {asset.ticker}, meta_updated_at={asset.meta_updated_at}")
                    time.sleep(1.1)
                except Exception as e:
                    print(f"[daily_asset_meta_job] 실패: {asset.ticker}, error={e}")
                    continue
        finally:
            db.close()

    scheduler.add_job(
        daily_asset_meta_job,
        trigger="cron",
        hour=9,
        minute=5,
        id="daily_asset_meta_refresh",
        replace_existing=True,
    )

    def daily_portfolio_snapshot_job():
        db: Session = SessionLocal()
        try:
            user_ids = [uid for (uid,) in db.query(User.id).all()]
            for user_id in user_ids:
                run_daily_portfolio_snapshot_for_user(db, user_id)
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    scheduler.add_job(
        daily_portfolio_snapshot_job,
        trigger="cron",
        hour=9,
        minute=10,
        id="daily_portfolio_snapshot",
        replace_existing=True,
    )

    scheduler.start()
    app.state.scheduler = scheduler
