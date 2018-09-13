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
    actions: Optional[List[Action]] = None
    image_url: Optional[str] = None
    thumb_url: Optional[str] = None
    footer: Optional[str] = None
    footer_icon: Optional[str] = None
    ts: Optional[int] = None

    def add_field(self, title: str, value: str, short: bool=False):
        self.fields.append(Field(title, value, short))

    def __str__(self) -> str:
        return f'Attachment(title={self.title!r})'


@attr.dataclass(slots=True)
class Confirmation:
    """Confirmation of Action"""

    dismiss_text: Optional[str] = None
    ok_text: Optional[str] = None
    text: Optional[str] = None
    title: Optional[str] = None


@attr.dataclass(slots=True)
class OptionField:
    """Optional Field on Action"""

    description: Optional[str] = None
    text: str
    value: str


@attr.dataclass(slots=True)
class Action:
    """Action of Attachment"""

    id: Optional[str] = None
    confirm: Optional[List[Confirmation]] = None
    data_source: Optional[str] = None
    min_query_length: Optional[int] = None
    name: Optional[str] = None
    options: Optional[List[OptionField]] = None
    selected_options: Optional[List[OptionField]] = None
    style: Optional[str] = None
    text: str
    type: str
    value: Optional[str] = None
    url: Optional[str] = None

