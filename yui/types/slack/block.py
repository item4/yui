import enum

from attrs import Factory
from attrs import define
from attrs import field

from ...utils.attrs import field_transformer
from ..base import ChannelID
from ..base import PublicChannelID
from ..base import UserID


class TextFieldType(enum.Enum):
    plain_text = "plain_text"
    mrkdwn = "mrkdwn"


@define(kw_only=True, field_transformer=field_transformer)
class TextField:
    text: str
    type: TextFieldType = TextFieldType.mrkdwn


def enforce_plain_text(instance, attribute, value):
    if value != TextFieldType.plain_text:
        raise ValueError("this field support only plain text")


@define(kw_only=True, field_transformer=field_transformer)
class PlainTextField(TextField):
    type: TextFieldType = field(
        validator=[enforce_plain_text],
        default=TextFieldType.plain_text,
    )


class Element:
    """Base class of Elements of Block Structure"""

    type: str


class InteractiveElement(Element):
    """Abstract class of interactive element classes"""


@define(kw_only=True, field_transformer=field_transformer)
class ImageElement(Element):
    image_url: str
    alt_text: str
    type: str = field(default="image", init=False)


class ButtonStyle(enum.Enum):
    default = "default"
    primary = "primary"
    danger = "danger"


@define(kw_only=True, field_transformer=field_transformer)
class ConfirmationDialog:
    title: PlainTextField
    text: TextField
    confirm: PlainTextField
    deny: PlainTextField


@define(kw_only=True, field_transformer=field_transformer)
class ButtonElement(InteractiveElement):
    text: TextField
    action_id: str
    url: str | None = None
    value: str | None = None
    style: ButtonStyle | None = ButtonStyle.default
    confirm: ConfirmationDialog | None = None
    type: str = field(default="button", init=False)


@define(kw_only=True, field_transformer=field_transformer)
class Option:
    text: PlainTextField
    value: str


@define(kw_only=True, field_transformer=field_transformer)
class OptionGroup:
    label: PlainTextField
    options: list[Option] = Factory(list)


@define(kw_only=True, field_transformer=field_transformer)
class StaticSelectElement(InteractiveElement):
    placeholder: PlainTextField
    action_id: str
    options: list[Option] = Factory(list)
    option_groups: list[OptionGroup] = Factory(list)
    initial_option: Option | None = None
    confirm: ConfirmationDialog | None = None
    type: str = field(default="static_select", init=False)


@define(kw_only=True, field_transformer=field_transformer)
class ExternalSelectElement(InteractiveElement):
    placeholder: PlainTextField
    action_id: str
    initial_option: Option | None = None
    confirm: ConfirmationDialog | None = None
    min_query_length: int | None = None
    type: str = field(default="external_select", init=False)


@define(kw_only=True, field_transformer=field_transformer)
class UsersSelectElement(InteractiveElement):
    placeholder: PlainTextField
    action_id: str
    initial_user: UserID | None = None
    confirm: ConfirmationDialog | None = None
    type: str = field(default="users_select", init=False)


@define(kw_only=True, field_transformer=field_transformer)
class ConversationsSelectElement(InteractiveElement):
    placeholder: PlainTextField
    action_id: str
    initial_conversation: ChannelID | None = None
    confirm: ConfirmationDialog | None = None
    type: str = field(default="conversations_select", init=False)


@define(kw_only=True, field_transformer=field_transformer)
class ChannelsSelectElement(InteractiveElement):
    placeholder: PlainTextField
    action_id: str
    initial_channel: PublicChannelID | None = None
    confirm: ConfirmationDialog | None = None
    type: str = field(default="channels_select", init=False)


@define(kw_only=True, field_transformer=field_transformer)
class OverflowElement(InteractiveElement):
    placeholder: PlainTextField
    action_id: str
    options: list[Option] = Factory(list)
    confirm: ConfirmationDialog | None = None
    type: str = field(default="overflow", init=False)


@define(kw_only=True, field_transformer=field_transformer)
class DatepickerElement(InteractiveElement):
    placeholder: PlainTextField
    action_id: str
    initial_date: str | None = None
    confirm: ConfirmationDialog | None = None
    type: str = field(default="datepicker", init=False)


class Block:
    """Slack Block Structure"""

    type: str = ""
    block_id: str | None = None


@define(kw_only=True, field_transformer=field_transformer)
class Section(Block):
    """Section Block"""

    text: TextField
    type: str = field(default="section", init=False)
    fields: list[TextField] = Factory(list)
    accessory: Element | None = None


@define(kw_only=True, field_transformer=field_transformer)
class Divider(Block):
    """Divider Block"""

    type: str = field(default="divider", init=False)


@define(kw_only=True, field_transformer=field_transformer)
class Image(Block):
    """Image Block"""

    image_url: str
    alt_text: str
    type: str = field(default="image", init=False)
    title: TextField | None = None


@define(kw_only=True, field_transformer=field_transformer)
class Action(Block):
    elements: list[InteractiveElement] = Factory(list)


@define(kw_only=True, field_transformer=field_transformer)
class Context(Block):
    """Context Block"""

    type: str = field(default="context", init=False)
    elements: list[TextField | ImageElement] = Factory(list)
