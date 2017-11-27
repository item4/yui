import six

try:
    from sqlalchemy.dialects.postgresql import JSON  # noqa
    has_postgres_json = True
except ImportError:
    has_postgres_json = False

from sqlalchemy_utils.types import JSONType as _JSONType

import ujson


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
