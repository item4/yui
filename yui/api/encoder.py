import enum

import attr

import ujson


def bool2str(value: bool) -> str:
    """Return bool as str."""

    if value:
        return '1'
    return '0'


def encode(obj):
    if isinstance(obj, (list, tuple, set)):
        return [encode(x) for x in obj]
    elif issubclass(obj.__class__, enum.Enum):
        return obj.value
    elif isinstance(obj, dict):
        return {
            encode(k): encode(v)
            for k, v in obj.items()
            if v is not None
        }
    elif isinstance(obj, bool):
        return bool2str(obj)
    try:
        return encode(attr.asdict(obj))
    except attr.exceptions.NotAnAttrsClassError:
        pass
    return obj


def to_json(obj) -> str:
    return ujson.dumps(encode(obj))
