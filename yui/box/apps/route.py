from __future__ import annotations

import html
from typing import Optional
from typing import TYPE_CHECKING
from typing import Union

from .base import BaseApp
from ..parsers import parse_option_and_arguments
from ..utils import SPACE_RE
from ..utils import split_chunks
from ...event import Event
from ...event import Message
from ...types.handler import HANDLER_CALL_TYPE
from ...types.handler import Handler
from ...utils.handler import get_handler

if TYPE_CHECKING:
    from ...bot import Bot


class Route:

    name: Optional[str]
    handler: Handler
    subtype: Optional[str] = None

    def __init__(
        self,
        name: Optional[str],
        callback: Union[HANDLER_CALL_TYPE, Handler],
        subtype: Optional[str] = None,
    ) -> None:
        self.name = name
        self.handler = get_handler(callback)
        self.subtype = subtype


class RouteApp(BaseApp):

    use_shlex: bool = True
    name: str
    route_list: list[Route] = []

    def get_short_help(self, prefix: str) -> str:
        raise NotImplementedError

    def get_full_help(self, prefix: str) -> str:
        return self.get_short_help(prefix)

    @property
    def names(self):
        return [self.name]

    async def fallback(self, bot: Bot, event: Message):
        pass

    async def run(self, bot: Bot, event: Event):
        if not isinstance(event, Message):
            return True

        root_args = ''
        root_call = ''
        args = ''
        handler = None
        if event.text:
            try:
                root_call, root_args = SPACE_RE.split(event.text, 1)
            except ValueError:
                root_call = event.text
        elif event.message and event.message.text:
            try:
                root_call, root_args = SPACE_RE.split(event.message.text, 1)
            except ValueError:
                root_call = event.message.text

        if root_call == bot.config.PREFIX + self.name:
            for c in self.route_list:
                if c.subtype == event.subtype or c.subtype == '*':
                    if root_args is None:
                        if c.name is None:
                            handler = c.handler
                            break
                    else:
                        try:
                            call, args = SPACE_RE.split(root_args, 1)
                        except ValueError:
                            call = root_args

                        if c.name == call:
                            handler = c.handler
                            break
            else:
                handler = Handler(self.fallback)

        if handler:
            raw = html.unescape(args)
            func_params = handler.params
            try:
                chunks = split_chunks(raw, self.use_shlex)
            except ValueError:
                await bot.say(
                    event.channel, '*Error*: Can not parse this command'
                )
                return False

            try:
                kw, remain_chunks = parse_option_and_arguments(
                    handler,
                    chunks,
                )
            except SyntaxError as e:
                await bot.say(event.channel, '*Error*\n{}'.format(e))
                return False
            with self.prepare_kwargs(
                bot=bot,
                event=event,
                func_params=func_params,
                **kw,
            ) as kwargs:
                return await handler(**kwargs)
        return True
