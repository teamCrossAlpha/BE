from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from common.database import SessionLocal
from sector_summary.service.daily_summary import (
    run_daily_sector_summary_for_user
)
from user.models import User  # 🔥 User 모델 import

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

    scheduler.start()
    app.state.scheduler = scheduler
