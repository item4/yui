from __future__ import annotations

import html
from typing import ClassVar
from typing import TYPE_CHECKING

from ...event import Event
from ...event import Message
from ...types.handler import HANDLER_CALL_TYPE
from ...types.handler import Handler
from ...utils.handler import get_handler
from ..parsers import parse_option_and_arguments
from ..utils import split_chunks
from .base import BaseApp

if TYPE_CHECKING:
    from ...bot import Bot


class Route:
    name: str | None
    handler: Handler
    subtype: str | None = None

    def __init__(
        self,
        name: str | None,
        callback: HANDLER_CALL_TYPE | Handler,
        subtype: str | None = None,
    ) -> None:
        self.name = name
        self.handler = get_handler(callback)
        self.subtype = subtype


class RouteApp(BaseApp):
    use_shlex: bool = True
    name: str
    route_list: ClassVar[list[Route]] = []

    def __getattribute__(self, item: str):
        obj = super().__getattribute__(item)
        if isinstance(obj, Handler) and obj.bound is None:
            obj.bound = self
        return obj

    def get_short_help(self, prefix: str) -> str:
        raise NotImplementedError

    def get_full_help(self, prefix: str) -> str:
        raise NotImplementedError

    @property
    def names(self) -> list[str]:
        return [self.name]

    async def fallback(self, bot: Bot, event: Message):
        raise NotImplementedError

    async def run(self, bot: Bot, event: Event):
        if not isinstance(event, Message):
            return True

        args = ""
        handler = None
        root_text = self.get_event_text(event)
        root_call, root_args = self.split_call_and_args(root_text)

        if root_call == bot.config.PREFIX + self.name:
            for c in self.route_list:
                event_subtype = getattr(event, "subtype", None)
                subtype_cond1 = c.subtype is None and event_subtype is None
                subtype_cond2 = (
                    c.subtype is not None
                    and event_subtype is not None
                    and c.subtype in {"*", event_subtype}
                )
                if subtype_cond1 or subtype_cond2:
                    if root_args:
                        call, args = self.split_call_and_args(root_args)

                        if c.name == call:
                            handler = c.handler
                            break
                    elif c.name is None:
                        handler = c.handler
                        break
            else:
                handler = Handler(f=self.fallback)

        if handler:
            raw = html.unescape(args)
            func_params = handler.params
            try:
                chunks = split_chunks(raw, self.use_shlex)
            except ValueError:
                await bot.say(
                    event.channel,
                    "*Error*: Can not parse this command",
                )
                return False

            try:
                kw, remain_chunks = parse_option_and_arguments(
                    handler,
                    chunks,
                )
            except SyntaxError as e:
                await bot.say(event.channel, f"*Error*\n{e}")
                return False
            async with self.prepare_kwargs(
                bot=bot,
                event=event,
                func_params=func_params,
                **kw,
            ) as kwargs:
                return await handler(**kwargs)
        return True
