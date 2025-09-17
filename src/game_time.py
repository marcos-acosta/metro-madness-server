from datetime import datetime, timedelta
import time
from zoneinfo import ZoneInfo
import math

from constants import NYC_TIME_ZONE


def now_epoch_millis() -> int:
    return math.floor(datetime.now().microsecond / 1000)


def epoch_time_to_seconds_since_midnight_est(epoch_time_seconds: int):
    dt_est = datetime.fromtimestamp(epoch_time_seconds, tz=ZoneInfo(NYC_TIME_ZONE))
    return make_seconds_since_midnight(dt_est)


def get_est_seconds_since_midnight() -> int:
    now_est = datetime.now(ZoneInfo(NYC_TIME_ZONE))
    return make_seconds_since_midnight(now_est)


def make_seconds_since_midnight(dt: datetime) -> int:
    last_midnight_est = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    return int((dt - last_midnight_est).total_seconds())


def get_est_hours_today() -> float:
    return get_est_seconds_since_midnight() / 3600


def get_current_week_str() -> str:
    now_est = datetime.now(ZoneInfo(NYC_TIME_ZONE))
    days_since_monday = now_est.weekday()
    latest_monday_est = now_est - timedelta(days=days_since_monday)
    return latest_monday_est.strftime("%Y-%m-%d")


def get_today_date_est_str() -> str:
    return datetime.now(ZoneInfo(NYC_TIME_ZONE)).strftime("%Y-%m-%d")


def minutes_since_epoch_seconds(epoch_seconds: int) -> float:
    return (int(time.time()) - epoch_seconds) / 60


def is_epoch_seconds_before_hour(epoch_seconds: int, hour: float) -> bool:
    return epoch_time_to_seconds_since_midnight_est(epoch_seconds) < hour * 3600
