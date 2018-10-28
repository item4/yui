from pytz import UTC, timezone
from pytz.tzinfo import BaseTzInfo

import six

try:
    from sqlalchemy.dialects.postgresql import JSON  # noqa
    has_postgres_json = True
except ImportError:
    has_postgres_json = False

from sqlalchemy_utils.types import JSONType as _JSONType
from sqlalchemy_utils.types import TimezoneType as _TimezoneType

import ujson

__all__ = (
    'JSONType',
    'TimezoneType',
)


class JSONType(_JSONType):
    """JSONType with ujson"""

    def process_bind_param(self, value, dialect):
        if dialect.name == 'postgresql' and has_postgres_json:
            return value
        if value is not None:
            value = six.text_type(ujson.dumps(value))
        return value

    def process_result_value(self, value, dialect):
        if dialect.name == 'postgresql':
            return value
        if value is not None:
            value = ujson.loads(value)
        return value


class TimezoneType(_TimezoneType):
    """TimezoneType with pytz correctly"""

    def __init__(self, backend='pytz'):
        self.backend = backend

        self.python_type = BaseTzInfo
        self._to = timezone
        self._from = six.text_type

    def _coerce(self, value):
        if value is not None and not isinstance(value, self.python_type):
            if value is UTC:
                return UTC
            obj = self._to(value)
            if obj is None:
                raise ValueError("unknown time zone '%s'" % value)
            return obj
        return value
