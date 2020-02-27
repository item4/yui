from __future__ import annotations

from typing import Dict, TYPE_CHECKING, Tuple

from ..types.handler import DECORATOR_ARGS_TYPE, Handler
from ..utils.handler import get_handler

if TYPE_CHECKING:
    from ._box import Box


class CronTask:
    """Cron Task"""

    handler: Handler

    def __init__(self, box: Box, spec: str, args: Tuple, kwargs: Dict) -> None:
        """Initialize."""

        if 'start' not in kwargs:
            kwargs['start'] = True

        self.box = box
        self.spec = spec
        self.args = args
        self.kwargs = kwargs
        self.start = None
        self.stop = None

    def __call__(self, target: DECORATOR_ARGS_TYPE) -> Handler:
        """Use as decorator"""

        handler = get_handler(target)

        self.handler = handler
        handler.cron = self

        return handler

    def __repr__(self) -> str:
        return (
            'CronTask('
            f'spec={self.spec!r}, '
            f'func={self.handler.f.__module__}.{self.handler.f.__name__}'
            ')'
        )

    __str__ = __repr__
