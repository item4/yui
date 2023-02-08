from collections.abc import Mapping
from typing import Any

from ...utils.attrs import define


@define
class APIResponse:
    body: dict[str, Any] | str
    status: int
    headers: Mapping[str, Any]

    def is_ok(self) -> bool:
        return isinstance(self.body, dict) and bool(self.body.get("ok"))
