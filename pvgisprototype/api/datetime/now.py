from datetime import datetime
from zoneinfo import ZoneInfo


def now_datetime() -> datetime:
    """Returns the current datetime in UTC.

    Return an aware timestamp using the local system time, however defaulting
    to UTC timezone.
    """
    return datetime.now()


def now_local_datetimezone():
    """Get current local date and time and zone"""
    print("[yellow]i[/yellow] Runnning the now_local_datetimezone() function!")
    return datetime.now().astimezone()


# Timezone


def now_utc_datetimezone() -> datetime:
    """Returns the current datetime in UTC.

    Return an aware timestamp using the local system time, however defaulting
    to UTC timezone.
    """
    return datetime.now(ZoneInfo("UTC"))
