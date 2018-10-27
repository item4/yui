import datetime as dt

from babel.dates import get_timezone


def now(tzname: str = 'Asia/Seoul') -> dt.datetime:
    """Helper to make current datetime."""

    return dt.datetime.now(tz=get_timezone(tzname))


def datetime(*args, tzname: str = 'Asia/Seoul') -> dt.datetime:
    return dt.datetime(*args).astimezone(get_timezone(tzname))
