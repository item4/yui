import re

__all__ = (
    'CONTAINER',
    'SPACE_RE',
    'is_container',
)

SPACE_RE = re.compile(r'\s+')

CONTAINER = (set, tuple, list)


def is_container(t) -> bool:
    """Check given value is container type?"""

    if hasattr(t, '__origin__'):
        return t.__origin__ in CONTAINER

    return t in CONTAINER
