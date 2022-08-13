import datetime as dt

from dateutil.tz import gettz


def now(tzname: str = "Asia/Seoul") -> dt.datetime:
    """Helper to make current datetime."""

    return dt.datetime.now(gettz(tzname))


def datetime(*args, tzname: str = "Asia/Seoul") -> dt.datetime:
    return dt.datetime(*args).replace(tzinfo=gettz(tzname))


def fromtimestamp(timestamp: float, tzname: str = "Asia/Seoul") -> dt.datetime:
    return dt.datetime.fromtimestamp(timestamp, tz=gettz(tzname))


def fromtimestampoffset(timestamp: float, offset: int) -> dt.datetime:
    tz = dt.timezone(dt.timedelta(seconds=offset))
    return dt.datetime.fromtimestamp(timestamp, tz=tz)


def fromisoformat(date_str: str, tzname: str = "Asia/Seoul") -> dt.datetime:
    return dt.datetime.fromisoformat(date_str).replace(
        tzinfo=gettz(tzname),
    )
