import datetime
from zoneinfo import ZoneInfo
from game_constants import WEEK_1_START_DATE


def get_now_est() -> datetime.datetime:
    return datetime.datetime.now(ZoneInfo("America/New_York"))


def get_today_est() -> datetime.date:
    return get_now_est().date()


def get_today_est_iso_format() -> str:
    return get_today_est().strftime("%Y-%m-%d")


def convert_datetime_to_seconds(d: datetime.datetime) -> int:
    return d.hour * 3600 + d.minute * 60 + d.second


def get_current_seconds_since_midnight_est() -> int:
    return convert_datetime_to_seconds(get_now_est())


def get_week_number(date: datetime.date) -> int:
    """
    Calculate the week number for a given date relative to WEEK_1_START_DATE.

    Both dates are assumed to be in EST timezone.

    Args:
        date: The date to calculate the week number for (assumed EST)

    Returns:
        The week number (1 for the first week, 2 for the second, etc.)
        Returns 0 or negative for dates before WEEK_1_START_DATE

    Example:
        If WEEK_1_START_DATE is 2025-10-20:
        - 2025-10-20 (day 0) -> week 1
        - 2025-10-26 (day 6) -> week 1
        - 2025-10-27 (day 7) -> week 2
        - 2025-10-19 (day -1) -> week 0
    """
    days_since_week_1 = (date - WEEK_1_START_DATE).days
    week_number = (days_since_week_1 // 7) + 1
    return week_number


def get_current_week_number() -> int:
    """
    Get the week number for the current date in EST timezone.

    This function gets the current time in EST (America/New_York timezone)
    and calculates which week number it corresponds to.

    Note: This automatically handles EST/EDT transitions (Daylight Saving Time).

    Returns:
        The current week number relative to WEEK_1_START_DATE
    """
    # Get current time in EST/EDT (America/New_York handles both)
    return get_week_number(get_today_est())
