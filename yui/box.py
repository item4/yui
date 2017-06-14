import collections
import functools
import inspect


__all__ = 'Box', 'Handler', 'box'


class Handler:
    """Handler"""

    def __init__(self, callback, *, need_prefix: bool=False):
        """Initialize"""

        self.callback = callback
        self.need_prefix = need_prefix
        self.signature = inspect.signature(callback)


class Box:
    """Box, collection of handlers and aliases"""

    def __init__(self):
        """Initialize"""

        self.handlers = collections.defaultdict(dict)
        self.aliases = {}

    def command(self, name: str, aliases=None):
        """Shortcut decorator for make command easily."""

        def decorator(func):
            while isinstance(func, Handler):
                func = func.callback

            @functools.wraps(func)
            def internal(func):
                self.handlers['message'][name] = Handler(
                    func,
                    need_prefix=True
                )

                if aliases is not None:
                    for alias in aliases:
                        self.aliases[alias] = name
            return internal(func)

        return decorator

    def on(self, type_: str):
        """Decorator for make handler."""

        def decorator(func):
            while isinstance(func, Handler):
                func = func.callback

            @functools.wraps(func)
            def internal(func):
                self.handlers[type_][func.__hash__] = Handler(func)

            return internal(func)

        return decorator


# (:class:`Box`) Default Box
box = Box()
