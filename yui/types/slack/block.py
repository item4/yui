import enum
from typing import Optional
from typing import Union

import attr

from ..base import ChannelID
from ..base import PublicChannelID
from ..base import UserID


class TextFieldType(enum.Enum):

    plain_text = 'plain_text'
    mrkdwn = 'mrkdwn'


@attr.dataclass(slots=True)
class TextField:

    text: str
    type: TextFieldType = attr.ib(default=TextFieldType.mrkdwn, kw_only=True)


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
    type: str = attr.ib(default='image', init=False)


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
    type: str = attr.ib(default='button', init=False)


@attr.dataclass(slots=True)
class Option:

    text: PlainTextField
    value: str


@attr.dataclass(slots=True)
class OptionGroup:

    label: PlainTextField
    options: list[Option] = attr.Factory(list)


@attr.dataclass(slots=True)
class StaticSelectElement(InteractiveElement):

    placeholder: PlainTextField
    action_id: str
    options: list[Option] = attr.Factory(list)
    option_groups: list[OptionGroup] = attr.Factory(list)
    initial_option: Optional[Option] = None
    confirm: Optional[ConfirmationDialog] = None
    type: str = attr.ib(default='static_select', init=False)


@attr.dataclass(slots=True)
class ExternalSelectElement(InteractiveElement):

    placeholder: PlainTextField
    action_id: str
    initial_option: Optional[Option] = None
    confirm: Optional[ConfirmationDialog] = None
    min_query_length: Optional[int] = None
    type: str = attr.ib(default='external_select', init=False)


@attr.dataclass(slots=True)
class UsersSelectElement(InteractiveElement):

    placeholder: PlainTextField
    action_id: str
    initial_user: Optional[UserID] = None
    confirm: Optional[ConfirmationDialog] = None
    type: str = attr.ib(default='users_select', init=False)


@attr.dataclass(slots=True)
class ConversationsSelectElement(InteractiveElement):

    placeholder: PlainTextField
    action_id: str
    initial_conversation: Optional[ChannelID] = None
    confirm: Optional[ConfirmationDialog] = None
    type: str = attr.ib(default='conversations_select', init=False)


@attr.dataclass(slots=True)
class ChannelsSelectElement(InteractiveElement):

    placeholder: PlainTextField
    action_id: str
    initial_channel: Optional[PublicChannelID] = None
    confirm: Optional[ConfirmationDialog] = None
    type: str = attr.ib(default='channels_select', init=False)


@attr.dataclass(slots=True)
class OverflowElement(InteractiveElement):

    placeholder: PlainTextField
    action_id: str
    options: list[Option] = attr.Factory(list)
    confirm: Optional[ConfirmationDialog] = None
    type: str = attr.ib(default='overflow', init=False)


@attr.dataclass(slots=True)
class DatepickerElement(InteractiveElement):

    placeholder: PlainTextField
    action_id: str
    initial_date: Optional[str] = None
    confirm: Optional[ConfirmationDialog] = None
    type: str = attr.ib(default='datepicker', init=False)


class Block:
    """Slack Block Structure"""

    type: str = ''
    block_id: Optional[str] = None


@attr.dataclass(slots=True)
class Section(Block):
    """Section Block"""

    text: TextField
    type: str = attr.ib(default='section', init=False)
    fields: list[TextField] = attr.Factory(list)
    accessory: Optional[Element] = None


@attr.dataclass(slots=True)
class Divider(Block):
    """Divider Block"""

    type: str = attr.ib(default='divider', init=False)


@attr.dataclass(slots=True)
class Image(Block):
    """Image Block"""

    image_url: str
    alt_text: str
    type: str = attr.ib(default='image', init=False)
    title: Optional[TextField] = None


@attr.dataclass(slots=True)
class Action(Block):

    elements: list[InteractiveElement] = attr.Factory(list)


@attr.dataclass(slots=True)
class Context(Block):
    """Context Block"""

    type: str = attr.ib(default='context', init=False)
    elements: list[Union[TextField, ImageElement]] = attr.Factory(list)
