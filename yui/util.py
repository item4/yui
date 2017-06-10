__all__ = 'AttrDict', 'bool2str'


def bool2str(value: bool) -> str:
    """Return bool as str."""

    if value:
        return 'true'
    return 'false'


class AttrDict(dict):
    """Helper object for attr get/set."""

    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, key, value):
        self[key] = value
