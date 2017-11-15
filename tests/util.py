from typing import Any, Dict, List, NamedTuple

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

    async def call(self, method: str, data: Dict[str, str]=None):
        self.call_queue.append(Call(method, data))


class FakeImportLib:
    """Fake object for importlib.import_module."""

    def __init__(self) -> None:
        self.import_queue: List[str] = []

    def import_module(self, path: str):
        self.import_queue.append(path)
