from typing import Any
from typing import ClassVar
from typing import Literal
from typing import NoReturn
from typing import TypeAlias
from typing import overload

from .types.base import ChannelID
from .types.base import Ts
from .types.base import UserID
from .types.namespace import BooleanField
from .types.namespace import ChannelField
from .types.namespace import Field
from .types.namespace import OptionalField
from .types.namespace import StringField
from .types.namespace import TsField
from .types.namespace import UserField
from .types.namespace import namespace
from .types.objects import MessageMessage


GoodByeType = Literal['goodbye']
HelloType = Literal['hello']
MessageType = Literal['message']
PongType = Literal['pong']
TeamJoinType = Literal['team_join']
TeamMigrationStartedType = Literal['team_migration_started']
YuiSystemStartType = Literal['yui_system_start']

EventType = Literal[
    GoodByeType,
    HelloType,
    MessageType,
    PongType,
    TeamJoinType,
    TeamMigrationStartedType,
    YuiSystemStartType,
]
Source: TypeAlias = dict[str, Any]


class BaseEvent:
    """Base class of Event."""


class Event(BaseEvent):
    """Event."""

    type: ClassVar[str]
    subtype: str | None = None


_events: dict[EventType, type[BaseEvent]] = {}


def event(cls):
    cls = namespace(cls)
    _events[cls.type] = cls
    return cls


@namespace
class UnknownEvent(BaseEvent):
    """Unknown Event."""

    type: str


@event
class GoodBye(Event):
    """The server intends to close the connection soon."""

    type: ClassVar[str] = 'goodbye'


@event
class Hello(Event):
    """The client has successfully connected to the server."""

    type: ClassVar[str] = 'hello'


@event
class Message(Event):
    """A message was sent to a channel."""

    type: ClassVar[str] = 'message'
    channel: ChannelID = ChannelField()
    ts: Ts = TsField(repr=True)
    event_ts: Ts = TsField()
    user: UserID = UserField(default=None)
    text: str = StringField(repr=True)
    attachments: list[dict[str, Any]] = Field()
    hidden: bool = BooleanField()
    message: MessageMessage = OptionalField(MessageMessage)(repr=True)
    subtype: str | None = OptionalField(str)(repr=True)


@event
class Pong(BaseEvent):
    """Ping-Pong"""

    type: ClassVar[str] = 'pong'


@event
class TeamJoin(Event):
    """A new team member has joined."""

    type: ClassVar[str] = 'team_join'
    user: UserID = UserField()


@event
class TeamMigrationStarted(Event):
    """The team is being migrated between servers."""

    type: ClassVar[str] = 'team_migration_started'


@event
class YuiSystemStart(Event):
    """System event for start system."""

    type: ClassVar[str] = 'yui_system_start'


@overload
def create_event(type_: GoodByeType, source: Source) -> GoodBye:
    ...


@overload
def create_event(type_: HelloType, source: Source) -> Hello:
    ...


@overload
def create_event(type_: MessageType, source: Source) -> Message:
    ...


@overload
def create_event(type_: PongType, source: Source) -> Pong:
    ...


@overload
def create_event(type_: TeamJoinType, source: Source) -> TeamJoin:
    ...


@overload
def create_event(
    type_: TeamMigrationStartedType, source: Source
) -> TeamMigrationStarted:
    ...


@overload
def create_event(type_: YuiSystemStartType, source: Source) -> YuiSystemStart:
    ...


@overload
def create_event(type_: str, source: Source) -> BaseEvent:
    ...


@overload
def create_event(type_: str, source: None) -> NoReturn:
    ...


def create_event(type_, source):
    """Create Event"""

    cls = _events.get(type_, UnknownEvent)

    try:
        return cls(type=type_, **source)
    except TypeError as e:
        raise TypeError(f'Error at creating {cls.__name__}: {e}')
