import collections
import functools
import inspect
from typing import (Any, Awaitable, Callable, Dict, List, Optional, Tuple,
                    Type, Union)

from .command import Argument, Option
from .event import Event
from .type import cast, is_container


__all__ = 'Box', 'Crontab', 'Handler', 'box'


class Handler:
    """Handler"""

    def __init__(
        self,
        callback,
        *,
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
        self.short_help = short_help
        self.help = help
        self.is_command = is_command
        self.use_shlex = use_shlex
        self.channel_validator = channel_validator
        self.signature = inspect.signature(callback)

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
                if argument.container_cls:
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
            Dict[Optional[str], Dict[str, Awaitable]]
        ] = collections.defaultdict(
            lambda: collections.defaultdict(dict)
        )
        self.aliases: Dict[
            Optional[str],
            Dict[str, str]
        ] = collections.defaultdict(dict)
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
                self.handlers['message'][subtype][name] = Handler(
                    func_,
                    short_help=_short_help,
                    help=help_message,
                    is_command=True,
                    use_shlex=use_shlex,
                    channel_validator=channels,
                )

                if aliases is not None:
                    for alias in aliases:
                        self.aliases[subtype][alias] = name

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

            name = f'{func.__module__}.{func.__name__}'

            @functools.wraps(func)
            def internal(func_):
                self.handlers[type_][subtype][name] = Handler(
                    func,
                    channel_validator=channels,
                )
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

    def __init__(self, box: Box, spec: str, args: Tuple, kwargs: Dict) -> None:
        """Initialize."""

        if 'start' not in kwargs:
            kwargs['start'] = True

        self.box = box
        self.spec = spec
        self.args = args
        self.kwargs = kwargs
        self.func: Callable = None
        self.start = None
        self.stop = None

    def __call__(self, func):
        """Use as decorator"""

        self.func = func

        return func

    def __str__(self) -> str:
        return f'Crontab(spec={self.spec!r}, ' \
               f'func={self.func.__module__}.{self.func.__name__})'


# (:class:`Box`) Default Box
box = Box()
