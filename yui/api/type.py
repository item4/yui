from typing import List, Optional

import attr

__all__ = 'Attachment', 'Field'


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
    fields: List[Field] = attr.Factory(list)
    image_url: Optional[str] = None
    thumb_url: Optional[str] = None
    footer: Optional[str] = None
    footer_icon: Optional[str] = None
    ts: Optional[int] = None

    def add_field(self, title: str, value: str, short: bool=False):
        self.fields.append(Field(title, value, short))

    def __str__(self) -> str:
        return f'Attachment(title={self.title!r})'
