from typing import Optional

from ..types.channel import PublicChannel
from ..types.user import User


def escape(text: str) -> str:
    """Make escaped text."""

    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def bold(text: str) -> str:
    """Make text to bold."""

    return f'*{text}*'


def italics(text: str) -> str:
    """Make text to italics."""

    return f'_{text}_'


def strike(text: str) -> str:
    """Make text to strike."""

    return f'~{text}~'


def code(text: str) -> str:
    """Make text to code."""

    return f'`{text}`'


def preformatted(text: str) -> str:
    """Make text to pre-formatted text."""

    return f'```{text}```'


def quote(text: str) -> str:
    """Make text to qoute."""

    return f'>{text}'


def link(x) -> str:
    if isinstance(x, User):
        return f'<@{x.id}>'
    elif isinstance(x, PublicChannel):
        return f'<#{x.id}>'
    elif isinstance(x, str):
        if x.startswith('U') or x.startswith('W'):
            return f'<@{x}>'
        elif x.startswith('C'):
            return f'<#{x}>'
        elif x.startswith('S'):
            return f'<!subteam^{x}>'
        return f'<{x}>'
    return f'<{x}>'


def link_url(url: str, text: Optional[str] = None) -> str:
    if text:
        return f'<{url}|{escape(text)}>'
    return f'<{url}>'


def link_here(text: str = 'here') -> str:
    return f'<!here|{escape(text)}>'


def link_channel(text: str = 'channel') -> str:
    return f'<!channel|{escape(text)}>'


def link_everyone(text: str = 'everyone') -> str:
    return f'<!everyone|{escape(text)}>'
