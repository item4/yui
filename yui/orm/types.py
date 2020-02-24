from dateutil.tz import UTC, gettz, tzfile

import six

try:
    from sqlalchemy.dialects.postgresql import JSON  # noqa
    has_postgres_json = True
except ImportError:  # pragma: no cover
    has_postgres_json = False

from sqlalchemy_utils.types import JSONType as _JSONType
from sqlalchemy_utils.types import TimezoneType as _TimezoneType

from ..utils import json


class JSONType(_JSONType):
    """JSONType with orjson"""

    def process_bind_param(self, value, dialect):
        if dialect.name == 'postgresql' and has_postgres_json:
            return value
        if value is not None:  # pragma: no cover
            value = six.text_type(json.dumps(value))
        return value  # pragma: no cover

    def process_result_value(self, value, dialect):
        if dialect.name == 'postgresql':
            return value
        if value is not None:  # pragma: no cover
            value = json.loads(value)
        return value  # pragma: no cover


class TimezoneType(_TimezoneType):
    """TimezoneType"""

    def __init__(self, backend='dateutil'):
        self.backend = backend

        self.python_type = tzfile
        self._to = gettz
        self._from = lambda x: x

    def _coerce(self, value):
        return value

    def process_bind_param(self, value, dialect):
        if value == UTC:
            return 'UTC'
        if isinstance(value, tzfile):
            return '/'.join(value._filename.split('/')[-2:])
        return value

    def process_result_value(self, value, dialect):
        if value == 'UTC':
            return UTC
        if value:
            return gettz(value)
        return None
