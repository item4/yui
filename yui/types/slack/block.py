import enum
from typing import List, Optional, Union

import attr

from ..base import ChannelID, PublicChannelID, UserID


class TextFieldType(enum.Enum):

    plain_text = 'plain_text'
    mrkdwn = 'mrkdwn'


@attr.dataclass(slots=True)
class TextField:

    text: str
    type: TextFieldType = TextFieldType.mrkdwn
    emoji: bool = True
    verbatim: bool = True


def enforce_plain_text(instance, attribute, value):
    if value != TextFieldType.plain_text:
        raise ValueError('this field support only plain text')


@attr.dataclass(slots=True)
class PlainTextField(TextField):

    type: TextFieldType = attr.ib(
        validator=[enforce_plain_text],
        default=TextFieldType.plain_text,
    )


class Element:
    """Base class of Elements of Block Structure"""

    type: str


class InteractiveElement(Element):
    """Abstract class of interactive element classes"""


@attr.dataclass(slots=True)
class ImageElement(Element):

    image_url: str
    alt_text: str
    type: str = 'image'


class ButtonStyle(enum.Enum):

    default = 'default'
    primary = 'primary'
    danger = 'danger'


@attr.dataclass(slots=True)
class ConfirmationDialog:

    title: PlainTextField
    text: TextField
    confirm: PlainTextField
    deny: PlainTextField


@attr.dataclass(slots=True)
class ButtonElement(InteractiveElement):

    text: TextField
    action_id: str
    url: Optional[str] = None
    value: Optional[str] = None
    style: Optional[ButtonStyle] = ButtonStyle.default
    confirm: Optional[ConfirmationDialog] = None
    type: str = 'button'


@attr.dataclass(slots=True)
class Option:

    text: PlainTextField
    value: str


@attr.dataclass(slots=True)
class OptionGroup:

    label: PlainTextField
    options: List[Option] = attr.Factory(list)


@attr.dataclass(slots=True)
class StaticSelectElement(InteractiveElement):

    placeholder: PlainTextField
    action_id: str
    options: List[Option] = attr.Factory(list)
    option_groups: List[OptionGroup] = attr.Factory(list)
    initial_option: Optional[Option] = None
    confirm: Optional[ConfirmationDialog] = None
    type: str = 'static_select'


@attr.dataclass(slots=True)
class ExternalSelectElement(InteractiveElement):

    placeholder: PlainTextField
    action_id: str
    initial_option: Optional[Option] = None
    confirm: Optional[ConfirmationDialog] = None
    min_query_length: Optional[int] = None
    type: str = 'external_select'


@attr.dataclass(slots=True)
class UsersSelectElement(InteractiveElement):

    placeholder: PlainTextField
    action_id: str
    initial_user: Optional[UserID] = None
    confirm: Optional[ConfirmationDialog] = None
    type: str = 'users_select'


@attr.dataclass(slots=True)
class ConversationsSelectElement(InteractiveElement):

    placeholder: PlainTextField
    action_id: str
    initial_conversation: Optional[ChannelID] = None
    confirm: Optional[ConfirmationDialog] = None
    type: str = 'conversations_select'


@attr.dataclass(slots=True)
class ChannelsSelectElement(InteractiveElement):

    placeholder: PlainTextField
    action_id: str
    initial_channel: Optional[PublicChannelID] = None
    confirm: Optional[ConfirmationDialog] = None
    type: str = 'channels_select'


@attr.dataclass(slots=True)
class OverflowElement(InteractiveElement):

    placeholder: PlainTextField
    action_id: str
    options: List[Option] = attr.Factory(list)
    confirm: Optional[ConfirmationDialog] = None
    type: str = 'overflow'


@attr.dataclass(slots=True)
class DatepickerElement(InteractiveElement):

    placeholder: PlainTextField
    action_id: str
    initial_date: Optional[str] = None
    confirm: Optional[ConfirmationDialog] = None
    type: str = 'datepicker'


class Block:
    """Slack Block Structure"""

    type: str = ''
    block_id: Optional[str] = None


@attr.dataclass(slots=True)
class Section(Block):
    """Section Block"""

    text: TextField
    type: str = 'section'
    fields: List[TextField] = attr.Factory(list)
    accessory: Optional[Element] = None


@attr.dataclass(slots=True)
class Divider(Block):
    """Divider Block"""

    type: str = 'divider'


@attr.dataclass(slots=True)
class Image(Block):
    """Image Block"""

    image_url: str
    alt_text: str
    type: str = 'image'
    title: Optional[TextField] = None


@attr.dataclass(slots=True)
class Action(Block):

    elements: List[InteractiveElement] = attr.Factory(list)


@attr.dataclass(slots=True)
class Context(Block):
    """Context Block"""

    elements: List[Union[TextField, ImageElement]] = attr.Factory(list)
