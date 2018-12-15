import asyncio
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import Callable, Dict, List, Optional, Union

import attr

from yui.api import SlackAPI
from yui.bot import Bot
from yui.config import Config, DEFAULT
from yui.event import Message
from yui.types.channel import (
    DirectMessageChannel,
    PrivateChannel,
    PublicChannel,
)
from yui.types.namespace import Namespace
from yui.types.user import User


@attr.dataclass(slots=True)
class Call:
    """API Call from bot"""

    method: str
    data: Optional[Dict[str, str]]
    token: Optional[str] = None


class FakeBot(Bot):
    """Fake bot for test"""

    def __init__(self, config: Config = None) -> None:
        if config is None:
            config = Config(**DEFAULT, TOKEN='asdf', CHANNELS={}, USERS={})

        Namespace._bot = self
        self.loop = asyncio.get_event_loop()
        self.call_queue: List[Call] = []
        self.api = SlackAPI(self)
        self.channels: List[PublicChannel] = []
        self.ims: List[DirectMessageChannel] = []
        self.groups: List[PrivateChannel] = []
        self.users: List[User] = [User(id='U0', team_id='T0', name='system')]
        self.responses: Dict[str, Callable] = {}
        self.config = config
        self.process_pool_executor = ProcessPoolExecutor()
        self.thread_pool_executor = ThreadPoolExecutor()

    async def call(
        self,
        method: str,
        data: Optional[Dict[str, str]] = None,
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

    def add_channel(
        self,
        id: str,
        name: str,
        creator: str = 'U0',
        last_read: int = 0,
    ):
        channel = PublicChannel(
            id=id,
            name=name,
            creator=creator,
            last_read=last_read,
        )
        self.channels.append(channel)
        return channel

    def add_private_channel(
        self,
        id: str,
        name: str,
        creator: str = 'U0',
        last_read: int = 0,
    ):
        channel = PrivateChannel(
            id=id,
            name=name,
            creator=creator,
            last_read=last_read,
        )
        self.groups.append(channel)
        return channel

    def add_dm(self, id: str, user: Union[User, str], last_read: int = 0):
        if isinstance(user, User):
            user_id = user.id
        else:
            user_id = user
        dm = DirectMessageChannel(id=id, user=user_id, last_read=last_read)
        self.ims.append(dm)
        return dm

    def add_user(self, id: str, name: str, team_id: str = 'T0'):
        user = User(id=id, name=name, team_id=team_id)
        self.users.append(user)
        return user

    def create_message(
        self,
        channel: Union[
            PublicChannel,
            PrivateChannel,
            DirectMessageChannel,
            str,
        ],
        user: Union[User, str],
        ts: str = '',
        event_ts: str = '',
        **kwargs,
    ) -> Message:
        if isinstance(channel, str):
            channel_id = channel
        else:
            channel_id = channel.id
        if isinstance(user, str):
            user_id = user
        else:
            user_id = user.id
        return Message(
            channel=channel_id,
            user=user_id,
            ts=ts,
            event_ts=event_ts,
            **kwargs,
        )


class FakeImportLib:
    """Fake object for importlib.import_module."""

    def __init__(self) -> None:
        self.import_queue: List[str] = []

    def import_module(self, path: str):
        self.import_queue.append(path)
