from attrs import Factory

from .action import Action
from .block import Block
from ...utils.attrs import define


@define(kw_only=False)
class Field:
    """Field on Attachment"""

    title: str
    value: str
    short: bool


@define
class Attachment:
    """Slack Attachment"""

    fallback: str | None = None
    color: str | None = None
    pretext: str | None = None
    author_name: str | None = None
    author_link: str | None = None
    author_icon: str | None = None
    title: str | None = None
    title_link: str | None = None
    text: str | None = None
    blocks: list[Block] | None = None
    fields: list[Field] = Factory(list)
    actions: list[Action] | None = None
    image_url: str | None = None
    thumb_url: str | None = None
    footer: str | None = None
    footer_icon: str | None = None
    ts: int | None = None
    callback_id: str | None = None
