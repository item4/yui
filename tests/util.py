from typing import Callable, Dict, List, NamedTuple

from yui.api import SlackAPI
from yui.bot import Bot
from yui.type import (
    BotLinkedNamespace,
    DirectMessageChannel,
    PrivateChannel,
    PublicChannel,
)


class Call(NamedTuple):
    """API Call from bot"""

    method: str
    data: Dict[str, str]


class FakeBot(Bot):
    """Fake bot for test"""

    def __init__(self) -> None:
        BotLinkedNamespace._bot = self
        self.call_queue: List[Call] = []
        self.api = SlackAPI(self)
        self.channels: List[PublicChannel] = []
        self.ims: List[DirectMessageChannel] = []
        self.groups: List[PrivateChannel] = []
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

    def add_channel(self, id: str, name: str):
        self.channels.append(PublicChannel(id=id, name=name))

    def add_private_channel(self, id: str, name: str):
        self.groups.append(PrivateChannel(id=id, name=name))

    def add_dm(self, id: str, user: str):
        self.ims.append(DirectMessageChannel(id=id, user=user))


class FakeImportLib:
    """Fake object for importlib.import_module."""

    def __init__(self) -> None:
        self.import_queue: List[str] = []

    def import_module(self, path: str):
        self.import_queue.append(path)
