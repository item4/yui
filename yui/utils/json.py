from typing import Any

import orjson


def loads(value: str) -> Any:
    return orjson.loads(value)


def dumps(value: Any) -> str:
    return orjson.dumps(value).decode()
