from __future__ import annotations

import asyncio
import contextlib
from typing import TYPE_CHECKING

from ..utils import SPACE_RE

if TYPE_CHECKING:
    import inspect
    from collections.abc import Mapping

    from ...bot import Bot
    from ...event import Event
    from ...event import Message


class BaseApp:
    """Base class of App"""

    def get_short_help(self, prefix: str) -> str:
        raise NotImplementedError

    def get_full_help(self, prefix: str) -> str:
        raise NotImplementedError

    @property
    def has_short_help(self) -> bool:
        raise NotImplementedError

    @property
    def has_full_help(self) -> bool:
        raise NotImplementedError

    async def run(self, bot: Bot, event: Event):
        raise NotImplementedError

    def get_event_text(self, event: Message) -> str:
        if event.text:
            return event.text
        if (
            event.message
            and hasattr(event.message, "text")
            and event.message.text
        ):
            return event.message.text
        return ""

    def split_call_and_args(self, text: str) -> tuple[str, str]:
        try:
            call, args = SPACE_RE.split(text, 1)
        except ValueError:
            call = text
            args = ""
        return call, args

    @contextlib.asynccontextmanager
    async def prepare_kwargs(
        self,
        *,
        bot: Bot,
        event: Event,
        func_params: Mapping[str, inspect.Parameter],
        **kwargs,
    ):
        sess = bot.session_maker()
        if "bot" in func_params:
            kwargs["bot"] = bot
        if "loop" in func_params:
            kwargs["loop"] = asyncio.get_running_loop()
        if "event" in func_params:
            kwargs["event"] = event
        if "sess" in func_params:
            kwargs["sess"] = sess

        try:
            yield kwargs
        finally:
            await sess.close()
