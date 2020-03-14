from __future__ import annotations

import html
import inspect
import shlex
from typing import List
from typing import Optional
from typing import TYPE_CHECKING

from .base import BaseApp
from ..parsers import parse_option_and_arguments
from ..utils import SPACE_RE
from ...command.validators import VALIDATOR_TYPE
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
        subtype: Optional[str],
        handler: Handler,
        *,
        name: Optional[str] = None,
        aliases: Optional[List[str]] = None,
        short_help: Optional[str] = None,
        help: Optional[str] = None,
        use_shlex: bool = False,
        is_command: bool = False,
        channel_validator: Optional[VALIDATOR_TYPE] = None,
    ) -> None:
        """Initialize"""
        self.type = type
        self.subtype = subtype
        self.handler = handler
        self.name = name
        self.aliases: List[str] = [] if aliases is None else aliases
        self.names: List[str] = self.aliases[:]

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
        self.channel_validator = channel_validator

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
        subtype = hasattr(event, 'subtype') and (
            event.subtype == self.subtype or self.subtype == '*'
        )
        if event.type == self.type and subtype:
            if isinstance(event, Message):
                return await self._run_message_event(bot, event)
            return await self._run(bot, event)
        return True

    async def _run(self, bot: Bot, event: Event):
        res: Optional[bool] = True
        validation = True
        if self.channel_validator and isinstance(event, Message):
            validation = await self.channel_validator(self, event)

        if validation:
            with self.prepare_kwargs(
                bot=bot, event=event, func_params=self.handler.params,
            ) as kwargs:
                res = await self.handler(**kwargs)

        return bool(res)

    async def _run_message_event(self, bot: Bot, event: Message):
        res: Optional[bool] = True
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
            if self.use_shlex:
                try:
                    chunks = shlex.split(raw)
                except ValueError:
                    await bot.say(
                        event.channel, '*Error*: Can not parse this command'
                    )
                    return False
            else:
                chunks = raw.split(' ')

            try:
                kw, remain_chunks = parse_option_and_arguments(
                    self.handler, chunks,
                )
            except SyntaxError as e:
                await bot.say(event.channel, '*Error*\n{}'.format(e))
                return False

            validation = True

            if self.channel_validator:
                validation = await self.channel_validator(self, event)

            if validation:
                if 'raw' in func_params:
                    kw['raw'] = raw
                if 'remain_chunks' in func_params:
                    annotation = func_params['remain_chunks'].annotation
                    if annotation in [str, inspect._empty]:  # type: ignore
                        kw['remain_chunks'] = ' '.join(remain_chunks)
                    else:
                        kw['remain_chunks'] = remain_chunks
                with self.prepare_kwargs(
                    bot=bot, event=event, func_params=func_params, **kw,
                ) as kwargs:
                    res = await self.handler(**kwargs)

        return bool(res)
