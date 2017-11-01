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
