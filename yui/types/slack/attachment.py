from typing import Optional

import attr

from .action import Action
from .block import Block


@attr.dataclass(slots=True)
class Field:
    """Field on Attachment"""

    title: str
    value: str
    short: bool


@attr.dataclass(slots=True)
class Attachment:
    """Slack Attachment"""

    fallback: Optional[str] = None
    color: Optional[str] = None
    pretext: Optional[str] = None
    author_name: Optional[str] = None
    author_link: Optional[str] = None
    author_icon: Optional[str] = None
    title: Optional[str] = None
    title_link: Optional[str] = None
    text: Optional[str] = None
    blocks: Optional[list[Block]] = None
    fields: list[Field] = attr.Factory(list)
    actions: Optional[list[Action]] = None
    image_url: Optional[str] = None
    thumb_url: Optional[str] = None
    footer: Optional[str] = None
    footer_icon: Optional[str] = None
    ts: Optional[int] = None
    callback_id: Optional[str] = None
