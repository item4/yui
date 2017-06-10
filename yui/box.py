import collections
import functools


class Box:
    """Box, collection of handlers and aliases"""

    def __init__(self):
        """Initialize"""

        self.handlers = collections.defaultdict(dict)
        self.aliases = {}

    def command(self, name: str, aliases=None):
        """Decorator to make command"""

        def decorator(func):
            @functools.wraps(func)
            def internal(func):
                self.handlers['message'][name] = func

                if aliases is not None:
                    for alias in aliases:
                        self.aliases[alias] = name
            return internal(func)

        return decorator


# (:class:`Box`) Default Box
box = Box()
