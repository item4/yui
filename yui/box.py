import collections
import functools
import inspect
import typing  # noqa: F401

from .command import Option  # noqa: F401


__all__ = 'Box', 'Handler', 'box'


class Handler:
    """Handler"""

    def __init__(self, callback, *, need_prefix: bool=False):
        """Initialize"""

        self.callback = callback
        self.need_prefix = need_prefix
        self.signature = inspect.signature(callback)

    def parse_option(self, chunk: typing.List[str]
                     ) -> typing.Tuple[typing.Dict, typing.List[str]]:

        end = False

        result = {}
        options: typing.List[Option] = getattr(
            self.callback,
            '__options__',
            []
        )
        required = {o.dest for o in options if o.required}

        for option in options:
            if option.multiple:
                result[option.dest] = []
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
                        args = [chunk.pop(0) for _ in range(option.nargs)]
                        try:
                            if isinstance(option.type_, type):
                                r = tuple(map(option.type_, args))
                            else:
                                r = option.type_(*args)
                        except ValueError as e:
                            raise SyntaxError(
                                'invalid type of option value({})'.format(e)
                            )

                        if len(r) != option.nargs:
                            raise SyntaxError(
                                ('incorrect option value count. '
                                 'expected {}, {} given.').format(
                                    option.nargs,
                                    len(r),
                                )
                            )
                        elif option.nargs == 1:
                            r = r[0]

                        if option.multiple:
                            result[option.dest].append(r)
                        else:
                            result[option.dest] = r

                    if option.dest in required:
                        required.remove(option.dest)

                    break

                chunk.insert(0, name)
            else:
                end = True

        for option in options:
            if not result[option.dest] and option.default is not None:
                result[option.dest] = option.default

        if required:
            raise SyntaxError('missing required options: {}'.format(required))

        return result, chunk


class Box:
    """Box, collection of handlers and aliases"""

    def __init__(self):
        """Initialize"""

        self.handlers = collections.defaultdict(
            lambda: collections.defaultdict(dict)
        )
        self.aliases = collections.defaultdict(dict)

    def command(self, name: str, aliases=None, *, subtype=None):
        """Shortcut decorator for make command easily."""

        def decorator(func):
            while isinstance(func, Handler):
                func = func.callback

            @functools.wraps(func)
            def internal(func_):
                self.handlers['message'][subtype][name] = Handler(
                    func,
                    need_prefix=True,
                )

                if aliases is not None:
                    for alias in aliases:
                        self.aliases[subtype][alias] = name
            return internal(func)

        return decorator

    def on(self, type_: str, *, subtype=None):
        """Decorator for make handler."""

        def decorator(func):
            while isinstance(func, Handler):
                func = func.callback

            @functools.wraps(func)
            def internal(func):
                self.handlers[type_][subtype][func.__name__] = Handler(
                    func,
                )

            return internal(func)

        return decorator


# (:class:`Box`) Default Box
box = Box()
