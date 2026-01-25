from datetime import date, datetime, time, timedelta

def get_summary_date() -> date:
    now = datetime.now()
    if now.time() < time(9, 0):
        return date.today() - timedelta(days=1)
    return date.today()
