from __future__ import annotations

import html
import inspect
from typing import TYPE_CHECKING

from .base import BaseApp
from ..parsers import parse_option_and_arguments
from ..utils import SPACE_RE
from ..utils import split_chunks
from ...event import Event
from ...event import Message
from ...types.handler import Handler
from ...utils.format import bold

if TYPE_CHECKING:
    from ...bot import Bot


class App(BaseApp):
    """Basic Handler"""

    def __init__(
        self,
        type: str,
        subtype: str | None,
        handler: Handler,
        *,
        name: str | None = None,
        aliases: list[str] | None = None,
        short_help: str | None = None,
        help: str | None = None,
        use_shlex: bool = False,
        is_command: bool = False,
    ) -> None:
        """Initialize"""
        self.type = type
        self.subtype = subtype
        self.handler = handler
        self.name = name
        self.aliases: list[str] = [] if aliases is None else aliases
        self.names: list[str] = self.aliases[:]

        if name:
            self.names.append(name)

        if short_help is None or help is None:
            doc = handler.doc
            if doc:
                if '\n\n' in doc:
                    short_help, help = doc.split('\n\n', 1)
                else:
                    if short_help is None:
                        short_help = doc

        self.short_help = short_help
        self.help = help
        self.is_command = is_command
        self.use_shlex = use_shlex

    @property
    def has_short_help(self) -> bool:
        return bool(self.short_help)

    @property
    def has_full_help(self) -> bool:
        return bool(self.short_help)

    def get_short_help(self, prefix: str) -> str:
        return f'`{prefix}{self.name}`: {self.short_help}'

    def get_full_help(self, prefix: str) -> str:
        aliases = '/'.join(
            f'`{prefix}{n}`' for n in self.names if self.name != n
        )

        help = bold(f'{prefix}{self.name}') + '\n'
        if aliases:
            help += f'(Aliases: {aliases})\n'

        help += str(self.short_help)

        if self.help:
            help += '\n\n' + self.help.format(PREFIX=prefix)
        return help

    async def run(self, bot: Bot, event: Event):
        subtype = (
            self.subtype
            and (event.subtype == self.subtype or self.subtype == '*')
        ) or not self.subtype
        if event.type == self.type and subtype:
            if isinstance(event, Message):
                return await self._run_message_event(bot, event)
            return await self._run(bot, event)
        return True

    async def _run(self, bot: Bot, event: Event):
        res: bool | None = True

        async with self.prepare_kwargs(
            bot=bot,
            event=event,
            func_params=self.handler.params,
        ) as kwargs:
            res = await self.handler(**kwargs)

        return bool(res)

    async def _run_message_event(self, bot: Bot, event: Message):
        res: bool | None = True
        call = ''
        args = ''
        if event.text:
            try:
                call, args = SPACE_RE.split(event.text, 1)
            except ValueError:
                call = event.text
        elif event.message and event.message.text:
            try:
                call, args = SPACE_RE.split(event.message.text, 1)
            except ValueError:
                call = event.message.text

        raw = html.unescape(args)

        match = True
        if self.is_command:
            match = any(
                call == bot.config.PREFIX + name for name in self.names
            )

        if match:
            func_params = self.handler.params
            try:
                chunks = split_chunks(raw, self.use_shlex)
            except ValueError:
                await bot.say(
                    event.channel, '*Error*: Can not parse this command'
                )
                return False

            try:
                kw, remain_chunks = parse_option_and_arguments(
                    self.handler,
                    chunks,
                )
            except SyntaxError as e:
                await bot.say(event.channel, '*Error*\n{}'.format(e))
                return False

            if 'raw' in func_params:
                kw['raw'] = raw
            if 'remain_chunks' in func_params:
                annotation = func_params['remain_chunks'].annotation
                if annotation in [str, inspect._empty]:
                    kw['remain_chunks'] = ' '.join(remain_chunks)
                else:
                    kw['remain_chunks'] = remain_chunks
            async with self.prepare_kwargs(
                bot=bot,
                event=event,
                func_params=func_params,
                **kw,
            ) as kwargs:
                res = await self.handler(**kwargs)

        return bool(res)
