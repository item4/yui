__all__ = 'bool2str'


def bool2str(value: bool) -> str:
    """Return bool as str."""

    if value:
        return 'true'
    return 'false'
