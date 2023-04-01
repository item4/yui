import datetime
from zoneinfo import ZoneInfo

from sqlalchemy.types import DateTime as _DateTime
from sqlalchemy.types import TypeDecorator

KST = ZoneInfo("Asia/Seoul")
UTC = datetime.UTC


class DateTime(TypeDecorator):
    impl = _DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if isinstance(value, datetime.datetime):
            if (
                value.tzinfo is not None
                and value.tzinfo.utcoffset(value) is not None
            ):
                value = value.astimezone(UTC)
            return value.replace(tzinfo=None)
        return value

    def process_result_value(self, value, dialect):
        if isinstance(value, datetime.datetime):
            return value.replace(tzinfo=UTC).astimezone(KST)
        return value
