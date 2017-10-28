from typing import Dict, List, NamedTuple

from yui.api import SlackAPI


class Call(NamedTuple):
    """API Call from bot"""

    method: str
    data: Dict[str, str]


class FakeBot:
    """Fake bot for test"""

    def __init__(self) -> None:
        self.call_queue: List[Call] = []
        self.api = SlackAPI(self)

    async def call(self, method: str, data: Dict[str, str]=None):
        self.call_queue.append(Call(method, data))
