from __future__ import annotations

import collections
import functools
import html
import inspect
import re
import shlex
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    TYPE_CHECKING,
    Tuple,
    Type,
    Union,
)

from .command import Argument, Option
from .event import Event, Message
from .orm import Session
from .type import cast, is_container

if TYPE_CHECKING:
    from .bot import Bot


__all__ = 'Box', 'Crontab', 'Handler', 'box'


SPACE_RE = re.compile('\s+')


class AbstractHandler:
    """Abstract Handler"""

    async def run(self, bot: Bot, event: Event):
        raise NotImplementedError


class Handler(AbstractHandler):
    """Handler"""

    def __init__(
        self,
        callback,
        *,
        name: Optional[str]=None,
        aliases: Optional[List[str]]=None,
        short_help: Optional[str]=None,
        help: Optional[str]=None,
        use_shlex: bool=False,
        is_command: bool=False,
        channel_validator: Optional[
            Callable[[Any, Event], Awaitable[bool]]
        ]=None
    ) -> None:
        """Initialize"""

        self.callback = callback
        self.name = name
        self.aliases: List[str] = [] if aliases is None else aliases
        self.names: List[str] = self.aliases[:]
        if name:
            self.names.append(name)

        self.short_help = short_help
        self.help = help
        self.is_command = is_command
        self.use_shlex = use_shlex
        self.channel_validator = channel_validator
        self.signature = inspect.signature(callback)

    async def run(self, bot: Bot, event: Event):
        if isinstance(event, Message):
            return await self._run_message_event(bot, event)
        else:
            return await self._run(bot, event)

    async def _run(self, bot: Bot, event: Event):
        func_params = self.signature.parameters
        kwargs: Dict[str, Any] = {}

        sess = Session(bind=bot.config.DATABASE_ENGINE)

        if 'bot' in func_params:
            kwargs['bot'] = bot
        if 'loop' in func_params:
            kwargs['loop'] = bot.loop
        if 'event' in func_params:
            kwargs['event'] = event
        if 'sess' in func_params:
            kwargs['sess'] = sess

        validation = True
        if self.channel_validator:
            validation = await self.channel_validator(self, event)

        if validation:
            try:
                res = await self.callback(**kwargs)
            finally:
                sess.close()
        else:
            sess.close()
            return True

        if not res:
            return False

        return True

    async def _run_message_event(self, bot: Bot, event: Message):
        call = ''
        args = ''
        if hasattr(event, 'text'):
            try:
                call, args = SPACE_RE.split(event.text, 1)
            except ValueError:
                call = event.text
        elif hasattr(event, 'message') and event.message and \
                hasattr(event.message, 'text'):
            try:
                call, args = SPACE_RE.split(event.message.text, 1)
            except ValueError:
                call = event.message.text

        match = True
        if self.is_command:
            match = any(
                call == bot.config.PREFIX + name for name in self.names
            )

        if match:
            func_params = self.signature.parameters
            kwargs = {}
            options: Dict[str, Any] = {}
            arguments: Dict[str, Any] = {}
            raw = html.unescape(args)
            if self.use_shlex:
                try:
                    option_chunks = shlex.split(raw)
                except ValueError:
                    await bot.say(
                        event.channel,
                        '*Error*: Can not parse this command'
                    )
                    return False
            else:
                option_chunks = raw.split(' ')

            try:
                options, argument_chunks = self.parse_options(option_chunks)
            except SyntaxError as e:
                await bot.say(event.channel, '*Error*\n{}'.format(e))
                return False

            try:
                arguments, remain_chunks = self.parse_arguments(
                    argument_chunks
                )
            except SyntaxError as e:
                await bot.say(event.channel, '*Error*\n{}'.format(e))
                return False
            else:
                kwargs.update(options)
                kwargs.update(arguments)

                sess = Session(bind=bot.config.DATABASE_ENGINE)

                if 'bot' in func_params:
                    kwargs['bot'] = bot
                if 'loop' in func_params:
                    kwargs['loop'] = bot.loop
                if 'event' in func_params:
                    kwargs['event'] = event
                if 'sess' in func_params:
                    kwargs['sess'] = sess
                if 'raw' in func_params:
                    kwargs['raw'] = raw
                if 'remain_chunks' in func_params:
                    annotation = func_params['remain_chunks'].annotation
                    if annotation in [str, inspect._empty]:  # type: ignore
                        kwargs['remain_chunks'] = ' '.join(remain_chunks)
                    else:
                        kwargs['remain_chunks'] = remain_chunks

                validation = True
                if self.channel_validator:
                    validation = await self.channel_validator(self, event)

                if validation:
                    try:
                        res = await self.callback(**kwargs)
                    finally:
                        sess.close()
                else:
                    sess.close()
                    return True

                if not res:
                    return False
        return True

    def parse_options(self, chunk: List[str]) -> Tuple[Dict, List[str]]:

        end = False

        result: Dict[str, Any] = {}
        options: List[Option] = self.callback.__options__

        for x in options:
            if x.type_ is None:
                type_ = self.signature.parameters[x.dest].annotation

                if type_ == inspect._empty:  # type: ignore
                    type_ = str
                else:
                    if x.transform_func:
                        type_ = str

                x.type_ = type_

        required = {o.dest for o in options if o.required}

        for option in options:
            if option.multiple:
                result[option.dest] = []
            else:
                if callable(option.default):
                    result[option.dest] = option.default()
                else:
                    result[option.dest] = option.default

        while not end and chunk:
            for option in options:
                name = chunk.pop(0)
                if name.startswith(option.name + '='):
                    name, new_chunk = name.split('=', 1)
                    chunk.insert(0, new_chunk)

                if name == option.name:
                    if option.nargs == 0:
                        result[option.dest] = option.value
                    else:
                        try:
                            length = len(chunk)
                            args = [chunk.pop(0) for _ in range(option.nargs)]
                        except IndexError:
                            raise SyntaxError(
                                option.count_error.format(
                                    name=option.name,
                                    expected=option.nargs,
                                    given=length,
                                )
                            )
                        try:
                            if option.container_cls:
                                if option.multiple:
                                    r = cast(option.type_, args)
                                else:
                                    r = option.container_cls(
                                        cast(option.type_, x) for x in args
                                    )
                            else:
                                r = cast(option.type_, args[0])
                        except ValueError as e:
                            raise SyntaxError(
                                option.type_error.format(name=option.name, e=e)
                            )

                        if option.transform_func:
                            if option.container_cls:
                                try:
                                    r = option.container_cls(
                                        option.transform_func(x)
                                        for x in r
                                    )
                                except ValueError as e:
                                    raise SyntaxError(
                                        option.transform_error.format(
                                            name=option.name,
                                            e=e,
                                        )
                                    )
                            else:
                                try:
                                    r = option.transform_func(r)
                                except ValueError as e:
                                    raise SyntaxError(
                                        option.transform_error.format(
                                            name=option.name,
                                            e=e,
                                        )
                                    )

                        if option.multiple:
                            result[option.dest].append(r[0])
                        else:
                            result[option.dest] = r

                    if option.dest in required:
                        required.remove(option.dest)

                    break

                chunk.insert(0, name)
            else:
                end = True

        if required:
            raise SyntaxError(
                '\n'.join(o.count_error.format(
                    name=o.name,
                    expected=o.nargs,
                    given=0,
                ) for o in (
                    list(filter(lambda x: x.dest == o, options))[0]
                    for o in required
                ))
            )

        return result, chunk

    def parse_arguments(self, chunk: List[str]) -> Tuple[Dict, List[str]]:

        result: Dict[str, Any] = {}

        arguments: List[Argument] = self.callback.__arguments__

        for x in arguments:
            if x.type_ is None:
                type_ = self.signature.parameters[x.dest].annotation

                if type_ == inspect._empty:  # type: ignore
                    type_ = str
                else:
                    if x.transform_func:
                        type_ = str

                x.type_ = type_
                if is_container(x.type_):
                    x.container_cls = None
                    x.typing_has_container = True

        for i, argument in enumerate(arguments):
            r = None
            length = argument.nargs
            if argument.nargs < 0:
                length = len(chunk) - sum(a.nargs for a in arguments[i:]) - 1

            if length < 1:
                raise SyntaxError(argument.count_error.format(
                    name=argument.name,
                    expected='>0',
                    given=0,
                ))
            if length <= len(chunk):
                args = [chunk.pop(0) for _ in range(length)]
            else:
                raise SyntaxError(argument.count_error.format(
                    name=argument.name,
                    expected=argument.nargs,
                    given=len(chunk),
                ))
            try:
                if argument.concat:
                    r = ' '.join(args)
                elif argument.container_cls:
                    r = argument.container_cls(
                        cast(argument.type_, x) for x in args
                    )
                elif argument.typing_has_container:
                    r = cast(argument.type_, args)
                else:
                    r = cast(argument.type_, args[0])
            except ValueError as e:
                raise SyntaxError(
                    argument.type_error.format(
                        name=argument.name,
                        e=e,
                    )
                )

            if argument.transform_func:
                if argument.container_cls and r:
                    try:
                        r = argument.container_cls(
                            argument.transform_func(x)
                            for x in r
                        )
                    except ValueError as e:
                        raise SyntaxError(argument.transform_error.format(
                            name=argument.name,
                            e=e,
                        ))
                else:
                    try:
                        r = argument.transform_func(r)
                    except ValueError as e:
                        raise SyntaxError(argument.transform_error.format(
                            name=argument.name,
                            e=e,
                        ))

            if r is not None:
                result[argument.dest] = r

        return result, chunk


class Box:
    """Box, collection of handlers and aliases"""

    def __init__(self) -> None:
        """Initialize"""

        self.handlers: Dict[
            Optional[str],
            Dict[Optional[str], List[AbstractHandler]]
        ] = collections.defaultdict(lambda: collections.defaultdict(list))
        self.crontabs: List[Crontab] = []

    def command(
        self,
        name: str,
        aliases: Optional[List[str]]=None,
        *,
        subtype: Optional[str]=None,
        short_help: Optional[str]=None,
        help: Optional[str]=None,
        use_shlex: bool=True,
        channels: Optional[
            Callable[[Any, Event], Awaitable[bool]]
        ]=None
    ):
        """Shortcut decorator for make command easily."""

        def decorator(func):
            _short_help = short_help
            help_message = help

            if not hasattr(func, '__arguments__'):
                func.__arguments__ = []
            if not hasattr(func, '__options__'):
                func.__options__ = []

            if help_message is None:
                doc = inspect.getdoc(func)
                if doc:
                    try:
                        _short_help, help_message = doc.split('\n\n', 1)
                    except ValueError:
                        _short_help = doc
                        help_message = None

                    _short_help = _short_help.replace('\n', ' ')

            @functools.wraps(func)
            def internal(func_):
                self.handlers['message'][subtype].append(Handler(
                    func_,
                    name=name,
                    aliases=aliases,
                    short_help=_short_help,
                    help=help_message,
                    is_command=True,
                    use_shlex=use_shlex,
                    channel_validator=channels,
                ))

                return func

            return internal(func)

        return decorator

    def on(
        self,
        type_: Union[str, Type[Event]],
        *,
        subtype: Optional[str]=None,
        channels: Optional[
            Callable[[Any, Event], Awaitable[bool]]
        ]=None
    ):
        """Decorator for make handler."""

        if not isinstance(type_, str):
            type_ = type_.type

        def decorator(func):
            if not hasattr(func, '__arguments__'):
                func.__arguments__ = []
            if not hasattr(func, '__options__'):
                func.__options__ = []

            @functools.wraps(func)
            def internal(func_):
                self.handlers[type_][subtype].append(Handler(
                    func,
                    channel_validator=channels,
                ))

                return func_

            return internal(func)

        return decorator

    def crontab(self, spec: str, *args, **kwargs):
        """Decorator for crontab job."""

        c = Crontab(self, spec, args, kwargs)
        self.crontabs.append(c)
        return c


class Crontab:
    """Crontab"""

    func: Callable

    def __init__(self, box: Box, spec: str, args: Tuple, kwargs: Dict) -> None:
        """Initialize."""

        if 'start' not in kwargs:
            kwargs['start'] = True

        self.box = box
        self.spec = spec
        self.args = args
        self.kwargs = kwargs
        self.start = None
        self.stop = None

    def __call__(self, func):
        """Use as decorator"""

        self.func = func
        setattr(func, '_crontab', self)

        return func

    def __str__(self) -> str:
        return f'Crontab(spec={self.spec!r}, ' \
               f'func={self.func.__module__}.{self.func.__name__})'


# (:class:`Box`) Default Box
box = Box()
