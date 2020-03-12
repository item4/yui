import enum
from typing import List, Optional, Union

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
    dismiss_text: Optional[str] = None
    ok_text: Optional[str] = None
    title: Optional[str] = None


@attr.dataclass(slots=True)
class OptionField:
    """Optional Option Field on Action"""

    text: str
    value: str
    description: Optional[str] = None


@attr.dataclass(slots=True)
class OptionFieldGroup:
    """Optional Option Group on Action"""

    text: str
    options: List[OptionField]


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
    type: Union[str, ActionType] = attr.ib(converter=ActionType)
    style: Optional[Union[str, ActionStyle]] = attr.ib(
        converter=call_or_none(ActionStyle),  # type: ignore
        default=None,
    )
    data_source: Optional[Union[str, ActionDataSource]] = attr.ib(
        converter=call_or_none(ActionDataSource),  # type: ignore
        default=None,
    )
    id: Optional[str] = None
    confirm: Optional[Confirmation] = None
    min_query_length: Optional[int] = None
    options: Optional[List[OptionField]] = None
    option_groups: Optional[List[OptionFieldGroup]] = None
    selected_options: Optional[List[OptionField]] = None
    value: Optional[str] = None
    url: Optional[str] = None

    def __attrs_post_init__(self):
        if self.data_source != ActionDataSource.external:
            self.min_query_length = None

        if self.options is not None and self.option_groups is not None:
            self.options = None
