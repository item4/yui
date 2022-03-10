import enum

import attr


def call_or_none(c):
    def converter(value):
        if value is None:
            return None
        return c(value)

    return converter


@attr.dataclass(slots=True)
class Confirmation:
    """Confirmation of Action"""

    text: str
    dismiss_text: str | None = None
    ok_text: str | None = None
    title: str | None = None


@attr.dataclass(slots=True)
class OptionField:
    """Optional Option Field on Action"""

    text: str
    value: str
    description: str | None = None


@attr.dataclass(slots=True)
class OptionFieldGroup:
    """Optional Option Group on Action"""

    text: str
    options: list[OptionField]


class ActionType(enum.Enum):

    button = 'button'
    select = 'select'


class ActionStyle(enum.Enum):

    default = 'default'
    primary = 'primary'
    danger = 'danger'


class ActionDataSource(enum.Enum):

    default = 'default'
    static = 'static'
    users = 'users'
    channels = 'channels'
    conversations = 'conversations'
    external = 'external'


@attr.dataclass(slots=True)
class Action:
    """Action of Attachment"""

    name: str
    text: str
    type: str | ActionType = attr.ib(converter=ActionType)
    style: str | ActionStyle | None = attr.ib(
        converter=call_or_none(ActionStyle),  # type: ignore
        default=None,
    )
    data_source: str | ActionDataSource | None = attr.ib(
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
