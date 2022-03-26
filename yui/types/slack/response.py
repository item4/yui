from collections.abc import Mapping
from typing import Any

from ...utils.attrs import define


@define
class APIResponse:

    body: dict[str, Any] | str
    status: int
    headers: Mapping[str, Any]
