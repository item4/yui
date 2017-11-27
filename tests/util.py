from typing import Any, Callable, Dict, List, NamedTuple

from yui.api import SlackAPI
from yui.bot import Bot


class Call(NamedTuple):
    """API Call from bot"""

    method: str
    data: Dict[str, str]


class FakeBot(Bot):
    """Fake bot for test"""

    def __init__(self) -> None:
        self.call_queue: List[Call] = []
        self.api = SlackAPI(self)
        self.channels: Dict[str, Dict[str, Any]] = {}
        self.responses: Dict[str, Callable] = {}

    async def call(self, method: str, data: Dict[str, str]=None):
        self.call_queue.append(Call(method, data))
        callback = self.responses.get(method)
        if callback:
            return callback(data)

    def response(self, method: str):
        def decorator(func):
            self.responses[method] = func
            return func
        return decorator


class FakeImportLib:
    """Fake object for importlib.import_module."""

    def __init__(self) -> None:
        self.import_queue: List[str] = []

    def import_module(self, path: str):
        self.import_queue.append(path)
