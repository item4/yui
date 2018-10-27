from ..types.namespace.linked import ChannelFromConfig, ChannelsFromConfig

__all__ = 'C', 'Cs'


class _C:
    """Magic class for create channel from config"""

    def __getattr__(self, key: str) -> ChannelFromConfig:
        return ChannelFromConfig(key)

    def __getitem__(self, key: str) -> ChannelFromConfig:
        return ChannelFromConfig(key)


class _Cs:
    """Magic class for create channels from config"""

    def __getattr__(self, key: str) -> ChannelsFromConfig:
        return ChannelsFromConfig(key)

    def __getitem__(self, key: str) -> ChannelsFromConfig:
        return ChannelsFromConfig(key)


# Magic instance for create channel from config
C = _C()

# Magic instance for create channels from config
Cs = _Cs()
