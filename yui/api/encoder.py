import enum

import attrs

from ..utils import json


def bool2str(value: bool) -> str:  # noqa: FBT001
    """Return bool as str."""

    if value:
        return "1"
    return "0"


def encode(obj):
    if isinstance(obj, (list, tuple, set)):
        return [encode(x) for x in obj]
    if issubclass(obj.__class__, enum.Enum):
        return obj.value
    if isinstance(obj, dict):
        return {encode(k): encode(v) for k, v in obj.items() if v is not None}
    if isinstance(obj, bool):
        return bool2str(obj)
    try:
        return encode(attrs.asdict(obj))
    except attrs.exceptions.NotAnAttrsClassError:
        pass
    return obj


def to_json(obj) -> str:
    return json.dumps(encode(obj))
