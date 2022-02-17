import asyncio
from contextlib import asynccontextmanager
from typing import Any
from typing import Callable
from typing import Optional
from typing import Union

import attr

from yui.api import SlackAPI
from yui.bot import Bot
from yui.cache import Cache
from yui.config import Config
from yui.config import DEFAULT
from yui.event import Message
from yui.types.channel import DirectMessageChannel
from yui.types.channel import PrivateChannel
from yui.types.channel import PublicChannel
from yui.types.namespace import Namespace
from yui.types.user import User


@attr.dataclass(slots=True)
class Call:
    """API Call from bot"""

    method: str
    data: Optional[dict[str, Any]]
    token: Optional[str] = None
    json_mode: bool = False


class FakeBot(Bot):
    """Fake bot for test"""

    def __init__(
        self,
        config: Config = None,
        *,
        loop=None,
        cache=None,
        process_pool_executor=None,
        thread_pool_executor=None,
    ) -> None:
        if config is None:
            config = Config(
                **DEFAULT,
                TOKEN='asdf',  # type: ignore
                CHANNELS={},
                USERS={},
            )

        Namespace._bot = self

        try:
            self.loop = loop or asyncio.get_running_loop()
        except RuntimeError:
            pass

        self.call_queue: list[Call] = []
        self.api = SlackAPI(self)
        self.channels: list[PublicChannel] = []
        self.ims: list[DirectMessageChannel] = []
        self.groups: list[PrivateChannel] = []
        self.cache: Cache = cache
        self.users: list[User] = [
            User(id='U0', team_id='T0', name='system'),  # type: ignore
        ]
        self.responses: dict[str, Callable] = {}
        self.config = config
        self.process_pool_executor = process_pool_executor
        self.thread_pool_executor = thread_pool_executor

    async def call(
        self,
        method: str,
        data: Optional[dict[str, Any]] = None,
        *,
        throttle_check: bool = False,
        token: Optional[str] = None,
        json_mode: bool = False,
    ):
        self.call_queue.append(Call(method, data, token, json_mode))
        callback = self.responses.get(method)
        if callback:
            return callback(data)

    @asynccontextmanager
    async def begin(self):
        try:
            yield
        finally:
            await self.cache.flush_all()

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
            id=id,  # type: ignore
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
            id=id,  # type: ignore
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
        dm = DirectMessageChannel(
            id=id,  # type: ignore
            user=user_id,
            last_read=last_read,
        )
        self.ims.append(dm)
        return dm

    def add_user(self, id: str, name: str, team_id: str = 'T0'):
        user = User(id=id, name=name, team_id=team_id)  # type: ignore
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
            channel=channel_id,  # type: ignore
            user=user_id,
            ts=ts,
            event_ts=event_ts,
            **kwargs,
        )


class FakeImportLib:
    """Fake object for importlib.import_module."""

    def __init__(self) -> None:
        self.import_queue: list[str] = []

    def import_module(self, path: str):
        self.import_queue.append(path)
