from __future__ import annotations

from typing import TYPE_CHECKING

from ..types.handler import FuncType
from ..types.handler import Handler

if TYPE_CHECKING:
    from ._box import Box


class CronTask:
    """Cron Task"""

    handler: Handler

    def __init__(self, box: Box, spec: str, args: tuple, kwargs: dict) -> None:
        """Initialize."""

        if "start" not in kwargs:
            kwargs["start"] = True

        self.box = box
        self.spec = spec
        self.args = args
        self.kwargs = kwargs
        self.start = None
        self.stop = None

    def __call__(self, target: FuncType | Handler) -> Handler:
        """Use as decorator"""

        handler = Handler.from_callable(target)

        self.handler = handler
        handler.cron = self

        return handler

    def __repr__(self) -> str:
        return f"CronTask(spec={self.spec!r}, func={self.handler!r})"

    __str__ = __repr__
