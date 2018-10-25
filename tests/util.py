import asyncio
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import Callable, Dict, List, NamedTuple, Optional

from yui.api import SlackAPI
from yui.bot import Bot
from yui.config import Config
from yui.type import (
    BotLinkedNamespace,
    DirectMessageChannel,
    PrivateChannel,
    PublicChannel,
    User,
)


class Call(NamedTuple):
    """API Call from bot"""

    method: str
    data: Dict[str, str]
    token: Optional[str]


class FakeBot(Bot):
    """Fake bot for test"""

    def __init__(self, config: Config = None) -> None:
        if config is None:
            config = Config()

        BotLinkedNamespace._bot = self
        self.loop = asyncio.get_event_loop()
        self.call_queue: List[Call] = []
        self.api = SlackAPI(self)
        self.channels: List[PublicChannel] = []
        self.ims: List[DirectMessageChannel] = []
        self.groups: List[PrivateChannel] = []
        self.users: Dict[str, User] = {}
        self.responses: Dict[str, Callable] = {}
        self.config = config
        self.process_pool_executor = ProcessPoolExecutor()
        self.thread_pool_executor = ThreadPoolExecutor()

    async def call(
        self,
        method: str,
        data: Dict[str, str] = None,
        *,
        token: Optional[str] = None,
    ):
        self.call_queue.append(Call(method, data, token))
        callback = self.responses.get(method)
        if callback:
            return callback(data)

    def response(self, method: str):
        def decorator(func):
            self.responses[method] = func
            return func
        return decorator

    def add_channel(self, id: str, name: str):
        channel = PublicChannel(id=id, name=name)
        self.channels.append(channel)
        return channel

    def add_private_channel(self, id: str, name: str):
        self.groups.append(PrivateChannel(id=id, name=name))

    def add_dm(self, id: str, user: str):
        self.ims.append(DirectMessageChannel(id=id, user=user))

    def add_user(self, id: str, name: str):
        self.users[id] = User(id=id, name=name)
        return self.users[id]


class FakeImportLib:
    """Fake object for importlib.import_module."""

    def __init__(self) -> None:
        self.import_queue: List[str] = []

    def import_module(self, path: str):
        self.import_queue.append(path)
