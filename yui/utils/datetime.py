import datetime as dt
from zoneinfo import ZoneInfo


def now(tzname: str = "Asia/Seoul") -> dt.datetime:
    """Helper to make current datetime."""

    return dt.datetime.now(ZoneInfo(tzname))


def datetime(
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
    tzname: str = "Asia/Seoul",
) -> dt.datetime:
    return dt.datetime(
        year, month, day, hour, minute, second, tzinfo=ZoneInfo(tzname)
    )


def fromtimestamp(timestamp: float, tzname: str = "Asia/Seoul") -> dt.datetime:
    return dt.datetime.fromtimestamp(timestamp, tz=ZoneInfo(tzname))


def fromtimestampoffset(timestamp: float, offset: int) -> dt.datetime:
    tz = dt.timezone(dt.timedelta(seconds=offset))
    return dt.datetime.fromtimestamp(timestamp, tz=tz)


def fromisoformat(date_str: str, tzname: str = "Asia/Seoul") -> dt.datetime:
    return dt.datetime.fromisoformat(date_str).replace(
        tzinfo=ZoneInfo(tzname),
    )
