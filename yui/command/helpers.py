from ..exceptions import AllChannelsError, NoChannelsError
from ..types.namespace import Namespace, name_convert


class HelperMeta(type):

    def __getattr__(cls, key):
        return cls(key)

    def __getitem__(cls, key):
        return cls(key)


class C(metaclass=HelperMeta):
    """Magic class for lazy access channel alias in config"""

    def __init__(self, key: str) -> None:
        self.key = key

    def get(self):
        channel_name = Namespace._bot.config.CHANNELS[self.key]
        if isinstance(channel_name, str):
            return name_convert(channel_name)
        raise ValueError(f'{self.key} in CHANNELS is not str.')


class Cs(metaclass=HelperMeta):
    """Magic class for lazy access channel list alias in config"""

    def __init__(self, key: str) -> None:
        self.key = key

    def gets(self):
        channels = Namespace._bot.config.CHANNELS[self.key]
        if not channels:
            raise NoChannelsError()
        if channels == ['*'] or channels == '*':
            raise AllChannelsError()
        if isinstance(channels, list):
            return [name_convert(x) for x in channels]
        raise ValueError(f'{self.key} in CHANNELS is not list.')
