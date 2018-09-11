from __future__ import annotations

import contextlib
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
    Mapping,
    NamedTuple,
    Optional,
    Set,
    TYPE_CHECKING,
    Tuple,
    Type,
    Union,
)

from .command import Argument, Option
from .event import Event, Message
from .orm import make_session
from .type import cast, is_container
from .util import bold

if TYPE_CHECKING:
    from .bot import Bot


__all__ = (
    'BaseHandler',
    'Box',
    'CommandMappingHandler',
    'CommandMappingUnit',
    'Crontab',
    'Handler',
    'box',
    'parse_option_and_arguments',
)


SPACE_RE = re.compile('\s+')

KWARGS_DICT = Dict[str, Any]


def parse_option_and_arguments(
    callback,
    chunks: List[str],
) -> Tuple[KWARGS_DICT, List[str]]:
    end = False

    result: KWARGS_DICT = {}
    options: List[Option] = getattr(callback, '__options__', [])
    arguments: List[Argument] = getattr(callback, '__arguments__', [])
    signature = inspect.signature(callback)

    for o in options:
        if o.type_ is None:
            type_ = signature.parameters[o.dest].annotation

            if type_ == inspect._empty:  # type: ignore
                type_ = str
            else:
                if o.transform_func:
                    type_ = str

            o.type_ = type_

    for a in arguments:
        if a.type_ is None:
            type_ = signature.parameters[a.dest].annotation

            if type_ == inspect._empty:  # type: ignore
                type_ = str
            else:
                if a.transform_func:
                    type_ = str

            a.type_ = type_
            if is_container(a.type_):
                a.container_cls = None
                a.typing_has_container = True

    required = {o.dest for o in options if o.required}

    for option in options:
        if option.multiple:
            result[option.dest] = []
        else:
            if callable(option.default):
                result[option.dest] = option.default()
            else:
                result[option.dest] = option.default

    while not end and chunks:
        for option in options:
            name = chunks.pop(0)
            if name.startswith(option.name + '='):
                name, new_chunk = name.split('=', 1)
                chunks.insert(0, new_chunk)

            if name == option.name:
                if option.dest in required:
                    required.remove(option.dest)

                if option.nargs == 0:
                    result[option.dest] = option.value
                    break

                length = len(chunks)
                try:
                    args = [chunks.pop(0) for _ in range(option.nargs)]
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

                break
            chunks.insert(0, name)
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

    for i, argument in enumerate(arguments):
        length = argument.nargs
        if argument.nargs < 0:
            length = len(chunks) - sum(a.nargs for a in arguments[i:]) - 1

        if length < 1:
            raise SyntaxError(argument.count_error.format(
                name=argument.name,
                expected='>0',
                given=0,
            ))
        if length <= len(chunks):
            args = [chunks.pop(0) for _ in range(length)]
        else:
            raise SyntaxError(argument.count_error.format(
                name=argument.name,
                expected=argument.nargs,
                given=len(chunks),
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

    return result, chunks


class BaseHandler:
    """Base class of Handler"""

    def get_short_help(self, prefix: str) -> str:
        raise NotImplementedError

    def get_full_help(self, prefix: str) -> str:
        return self.get_short_help(prefix)

    @property
    def has_short_help(self) -> bool:
        try:
            self.get_short_help('')
        except NotImplementedError:
            return False
        return True

    @property
    def has_full_help(self) -> bool:
        try:
            self.get_full_help('')
        except NotImplementedError:
            return False
        return True

    async def run(self, bot: Bot, event: Event):
        raise NotImplementedError

    @contextlib.contextmanager
    def prepare_kwargs(
        self,
        *,
        bot: Bot,
        event: Event,
        func_params: Mapping[str, inspect.Parameter],
        **kwargs,
    ):
        sess = make_session(bind=bot.config.DATABASE_ENGINE)
        if 'bot' in func_params:
            kwargs['bot'] = bot
        if 'loop' in func_params:
            kwargs['loop'] = bot.loop
        if 'event' in func_params:
            kwargs['event'] = event
        if 'sess' in func_params:
            kwargs['sess'] = sess

        yield kwargs

        sess.close()


class CommandMappingUnit(NamedTuple):

    name: Optional[str]
    callback: Callable[..., Awaitable]
    subtype: Optional[str] = None


class CommandMappingHandler(BaseHandler):

    use_shlex: bool = True
    name: str
    command_map: List[CommandMappingUnit] = []

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
        command = None
        if hasattr(event, 'text'):
            try:
                root_call, root_args = SPACE_RE.split(event.text, 1)
            except ValueError:
                root_call = event.text
        elif hasattr(event, 'message') and event.message and \
                hasattr(event.message, 'text'):
            try:
                root_call, root_args = SPACE_RE.split(event.message.text, 1)
            except ValueError:
                root_call = event.message.text

        if root_call == bot.config.PREFIX + self.name:
            for c in self.command_map:
                if c.subtype == event.subtype:
                    if root_args is None:
                        if c.name is None:
                            command = c.callback
                            break
                    else:
                        try:
                            call, args = SPACE_RE.split(root_args, 1)
                        except ValueError:
                            call = root_args

                        if c.name == call:
                            command = c.callback
                            break
            else:
                command = self.fallback

        if command:
            raw = html.unescape(args)
            func_params = inspect.signature(command).parameters
            if self.use_shlex:
                try:
                    chunks = shlex.split(raw)
                except ValueError:
                    await bot.say(
                        event.channel,
                        '*Error*: Can not parse this command'
                    )
                    return False
            else:
                chunks = raw.split(' ')

            try:
                kw, remain_chunks = parse_option_and_arguments(
                    command,
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
            ) as kwargs:  # type: KWARGS_DICT
                return await command(**kwargs)
        return True


class Handler(BaseHandler):
    """Handler"""

    def __init__(
        self,
        type: str,
        subtype: Optional[str],
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
        self.type = type
        self.subtype = subtype
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

    @property
    def has_short_help(self) -> bool:
        return bool(self.short_help)

    @property
    def has_full_help(self) -> bool:
        return bool(self.short_help)

    def get_short_help(self, prefix: str) -> str:
        return f'`={self.name}`: {self.short_help}'

    def get_full_help(self, prefix: str) -> str:
        aliases = '/'.join(
            f'`{prefix}{n}`' for n in self.names if self.name != n
        )

        help = bold(f'={self.name}') + '\n'
        if aliases:
            help += f'(Aliases: {aliases})\n'

        help += str(self.short_help)

        if self.help:
            help += '\n\n' + self.help.format(PREFIX=prefix)
        return help

    async def run(self, bot: Bot, event: Event):
        if event.type == self.type and event.subtype == self.subtype:
            if isinstance(event, Message):
                return await self._run_message_event(bot, event)
            return await self._run(bot, event)
        return True

    async def _run(self, bot: Bot, event: Event):
        res = True
        validation = True
        if self.channel_validator:
            validation = await self.channel_validator(self, event)

        if validation:
            with self.prepare_kwargs(
                bot=bot,
                event=event,
                func_params=inspect.signature(self.callback).parameters,
            ) as kwargs:  # type: KWARGS_DICT
                res = await self.callback(**kwargs)

        return bool(res)

    async def _run_message_event(self, bot: Bot, event: Message):
        res = True
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

        raw = html.unescape(args)

        match = True
        if self.is_command:
            match = any(
                call == bot.config.PREFIX + name for name in self.names
            )

        if match:
            func_params = inspect.signature(self.callback).parameters
            if self.use_shlex:
                try:
                    chunks = shlex.split(raw)
                except ValueError:
                    await bot.say(
                        event.channel,
                        '*Error*: Can not parse this command'
                    )
                    return False
            else:
                chunks = raw.split(' ')

            try:
                kw, remain_chunks = parse_option_and_arguments(
                    self.callback,
                    chunks,
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
                        kw['remain_chunks'] = ' '.join(
                            remain_chunks
                        )
                    else:
                        kw['remain_chunks'] = remain_chunks
                with self.prepare_kwargs(
                    bot=bot,
                    event=event,
                    func_params=func_params,
                    **kw,
                ) as kwargs:  # type: KWARGS_DICT
                    res = await self.callback(**kwargs)

        return bool(res)


class Box:
    """Box, collection of handlers and aliases"""

    def __init__(self) -> None:
        """Initialize"""

        self.config_required: Dict[str, Any] = {}
        self.channel_required: Set[str] = set()
        self.channels_required: Set[str] = set()
        self.handlers: List[BaseHandler] = []
        self.crontabs: List[Crontab] = []

    def register(self, handler: BaseHandler):
        """Register Handler manually."""

        self.handlers.append(handler)

    def assert_config_required(self, key: str, type):
        """Mark required configuration key and type."""

        self.config_required[key] = type

    def assert_channel_required(self, key: str):
        """Mark required channel name in configuration."""

        self.channel_required.add(key)

    def assert_channels_required(self, key: str):
        """Mark required channels name in configuration."""

        self.channels_required.add(key)

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
                self.handlers.append(Handler(
                    'message',
                    subtype,
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
                self.handlers.append(Handler(
                    type_,
                    subtype,
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
