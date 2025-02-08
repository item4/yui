from __future__ import annotations

import asyncio
import random
from contextlib import asynccontextmanager
from typing import Any
from typing import TYPE_CHECKING

from attrs import define

from yui.api import SlackAPI
from yui.bot import Bot
from yui.box import Box
from yui.config import Config
from yui.config import DEFAULT
from yui.event import Message
from yui.types.base import PublicChannelID
from yui.types.base import Ts
from yui.types.base import UserID
from yui.types.channel import PublicChannel
from yui.types.user import User

if TYPE_CHECKING:
    from collections.abc import Callable

    from yui.cache import Cache


@define
class Call:
    """API Call from bot"""

    method: str
    data: dict[str, Any] | None
    token: str | None = None
    json_mode: bool = False


class FakeBot(Bot):
    """Fake bot for test"""

    def __init__(
        self,
        config: Config | None = None,
        *,
        using_box: Box | None = None,
        cache=None,
        process_pool_executor=None,
        thread_pool_executor=None,
    ) -> None:
        if config is None:
            config = Config(
                **DEFAULT,
                APP_TOKEN="TEST_APP_TOKEN",  # noqa: S106
                BOT_TOKEN="TEST_BOT_TOKEN",  # noqa: S106
                CHANNELS={},
                USERS={},
            )

        if using_box is None:
            using_box = Box()

        self.call_queue: list[Call] = []
        self.api = SlackAPI(self)
        self.cache: Cache = cache
        self.responses: dict[str, Callable] = {}
        self.config = config
        self.box = using_box
        self.is_ready = asyncio.Event()
        self.process_pool_executor = process_pool_executor
        self.thread_pool_executor = thread_pool_executor

    async def call(
        self,
        method: str,
        data: dict[str, Any] | None = None,
        *,
        throttle_check: bool = False,
        token: str | None = None,
        json_mode: bool = False,
    ):
        self.call_queue.append(Call(method, data, token, json_mode))
        callback = self.responses.get(method)
        if callback:
            return callback(data)
        return None

    @asynccontextmanager
    async def begin(self):
        try:
            yield
        finally:
            await self.cache.flushall()

    def response(self, method: str):
        def decorator(func):
            self.responses[method] = func
            return func

        return decorator

    def create_channel(
        self,
        id: str,
        name: str,
        creator: str = "U0",
        last_read: str = "0",
    ) -> PublicChannel:
        return PublicChannel(
            id=PublicChannelID(id),
            name=name,
            creator=UserID(creator),
            last_read=Ts(last_read),
        )

    def create_user(self, id: str, name: str) -> User:
        return User(id=UserID(id), name=name)

    def create_message(
        self,
        *,
        channel_id: str | None = None,
        user_id: str | None = None,
        ts: str = "",
        event_ts: str = "",
        **kwargs,
    ) -> Message:
        if channel_id is None:
            channel_id = "C" + str(random.randint(0, 99999)).zfill(5)
        if user_id is None:
            user_id = "U" + str(random.randint(0, 99999)).zfill(5)
        return Message(
            channel=PublicChannelID(channel_id),
            user=UserID(user_id),
            ts=Ts(ts),
            event_ts=Ts(event_ts),
            **kwargs,
        )


class FakeImportLib:
    """Fake object for importlib.import_module."""

    def __init__(self) -> None:
        self.import_queue: list[str] = []

    def import_module(self, path: str):
        self.import_queue.append(path)
