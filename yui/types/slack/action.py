import enum

from attrs import field

from ...utils.attrs import define


def call_or_none(c):
    def converter(value):
        if value is None:
            return None
        return c(value)

    return converter


@define
class Confirmation:
    """Confirmation of Action"""

    text: str
    dismiss_text: str | None = None
    ok_text: str | None = None
    title: str | None = None


@define
class OptionField:
    """Optional Option Field on Action"""

    text: str
    value: str
    description: str | None = None


@define
class OptionFieldGroup:
    """Optional Option Group on Action"""

    text: str
    options: list[OptionField]


class ActionType(enum.Enum):

    button = "button"
    select = "select"


class ActionStyle(enum.Enum):

    default = "default"
    primary = "primary"
    danger = "danger"


class ActionDataSource(enum.Enum):

    default = "default"
    static = "static"
    users = "users"
    channels = "channels"
    conversations = "conversations"
    external = "external"


@define
class Action:
    """Action of Attachment"""

    name: str
    text: str
    type: str | ActionType = field(converter=ActionType)
    style: str | ActionStyle | None = field(
        converter=call_or_none(ActionStyle),  # type: ignore
        default=None,
    )
    data_source: str | ActionDataSource | None = field(
        converter=call_or_none(ActionDataSource),  # type: ignore
        default=None,
    )
    id: str | None = None
    confirm: Confirmation | None = None
    min_query_length: int | None = None
    options: list[OptionField] | None = None
    option_groups: list[OptionFieldGroup] | None = None
    selected_options: list[OptionField] | None = None
    value: str | None = None
    url: str | None = None

    def __attrs_post_init__(self):
        if self.data_source != ActionDataSource.external:
            self.min_query_length = None

        if self.options is not None and self.option_groups is not None:
            self.options = None
