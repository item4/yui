from collections.abc import Mapping
from typing import Any

import attr


@attr.dataclass(slots=True)
class APIResponse:

    body: dict[str, Any] | str
    status: int
    headers: Mapping[str, Any]
