import enum

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
    url: str | None = None
    value: str | None = None
    style: ButtonStyle | None = ButtonStyle.default
    confirm: ConfirmationDialog | None = None
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
    initial_option: Option | None = None
    confirm: ConfirmationDialog | None = None
    type: str = attr.ib(default='static_select', init=False)


@attr.dataclass(slots=True)
class ExternalSelectElement(InteractiveElement):

    placeholder: PlainTextField
    action_id: str
    initial_option: Option | None = None
    confirm: ConfirmationDialog | None = None
    min_query_length: int | None = None
    type: str = attr.ib(default='external_select', init=False)


@attr.dataclass(slots=True)
class UsersSelectElement(InteractiveElement):

    placeholder: PlainTextField
    action_id: str
    initial_user: UserID | None = None
    confirm: ConfirmationDialog | None = None
    type: str = attr.ib(default='users_select', init=False)


@attr.dataclass(slots=True)
class ConversationsSelectElement(InteractiveElement):

    placeholder: PlainTextField
    action_id: str
    initial_conversation: ChannelID | None = None
    confirm: ConfirmationDialog | None = None
    type: str = attr.ib(default='conversations_select', init=False)


@attr.dataclass(slots=True)
class ChannelsSelectElement(InteractiveElement):

    placeholder: PlainTextField
    action_id: str
    initial_channel: PublicChannelID | None = None
    confirm: ConfirmationDialog | None = None
    type: str = attr.ib(default='channels_select', init=False)


@attr.dataclass(slots=True)
class OverflowElement(InteractiveElement):

    placeholder: PlainTextField
    action_id: str
    options: list[Option] = attr.Factory(list)
    confirm: ConfirmationDialog | None = None
    type: str = attr.ib(default='overflow', init=False)


@attr.dataclass(slots=True)
class DatepickerElement(InteractiveElement):

    placeholder: PlainTextField
    action_id: str
    initial_date: str | None = None
    confirm: ConfirmationDialog | None = None
    type: str = attr.ib(default='datepicker', init=False)


class Block:
    """Slack Block Structure"""

    type: str = ''
    block_id: str | None = None


@attr.dataclass(slots=True)
class Section(Block):
    """Section Block"""

    text: TextField
    type: str = attr.ib(default='section', init=False)
    fields: list[TextField] = attr.Factory(list)
    accessory: Element | None = None


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
    title: TextField | None = None


@attr.dataclass(slots=True)
class Action(Block):

    elements: list[InteractiveElement] = attr.Factory(list)


@attr.dataclass(slots=True)
class Context(Block):
    """Context Block"""

    type: str = attr.ib(default='context', init=False)
    elements: list[TextField | ImageElement] = attr.Factory(list)
