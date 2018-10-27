import datetime

from babel.dates import get_timezone


def now(tzname: str = 'Asia/Seoul') -> datetime.datetime:
    """Helper to make current datetime."""

    return datetime.datetime.now(tz=get_timezone(tzname))
