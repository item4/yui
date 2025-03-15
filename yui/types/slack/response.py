from collections.abc import Mapping
from typing import Any

from attrs import define

from ...utils.attrs import field_transformer


@define(kw_only=True, field_transformer=field_transformer)
class APIResponse:
    body: dict[str, Any]
    status: int
    headers: Mapping[str, Any]

    def is_ok(self) -> bool:
        return isinstance(self.body, dict) and bool(self.body.get("ok"))
