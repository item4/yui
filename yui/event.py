from typing import Any
from typing import ClassVar
from typing import Literal
from typing import TypeAlias
from typing import overload

from .types.base import ChannelID
from .types.base import Ts
from .types.base import UserID
from .types.objects import MessageMessage
from .utils.attrs import channel_id_field
from .utils.attrs import define
from .utils.attrs import field
from .utils.attrs import make_instance
from .utils.attrs import ts_field
from .utils.attrs import user_id_field

GoodByeType = Literal["goodbye"]
HelloType = Literal["hello"]
MessageType = Literal["message"]
PongType = Literal["pong"]
TeamJoinType = Literal["team_join"]
TeamMigrationStartedType = Literal["team_migration_started"]
YuiSystemStartType = Literal["yui_system_start"]

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


class Event:
    """Base class of Event."""

    type: ClassVar[str]
    subtype: str | None


_events: dict[EventType, type[Event]] = {}


def event(cls):
    _events[cls.type] = cls
    return cls


@define
class UnknownEvent:
    """Unknown Event."""

    type: str


@event
@define
class GoodBye(Event):
    """The server intends to close the connection soon."""

    type: ClassVar[str] = "goodbye"


@event
@define
class Hello(Event):
    """The client has successfully connected to the server."""

    type: ClassVar[str] = "hello"


@event
@define
class Message(Event):
    """A message was sent to a channel."""

    type: ClassVar[str] = "message"
    channel: ChannelID = channel_id_field()
    ts: Ts = ts_field()
    event_ts: Ts = ts_field(repr=False)
    user: UserID = user_id_field(default=None)
    text: str = field(repr=True)
    attachments: list[dict[str, Any]] | None = field()
    hidden: bool = field()
    message: MessageMessage | None = field(repr=True)
    subtype: str | None = field(repr=True)


@event
@define
class Pong(Event):
    """Ping-Pong"""

    type: ClassVar[str] = "pong"


@event
@define
class TeamJoin(Event):
    """A new team member has joined."""

    type: ClassVar[str] = "team_join"
    user: UserID = user_id_field()


@event
@define
class TeamMigrationStarted(Event):
    """The team is being migrated between servers."""

    type: ClassVar[str] = "team_migration_started"


@event
@define
class YuiSystemStart(Event):
    """System event for start system."""

    type: ClassVar[str] = "yui_system_start"


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


def create_event(type_, source):
    """Create Event"""

    cls = _events.get(type_, UnknownEvent)

    try:
        if cls is UnknownEvent:
            source["type"] = type_
        return make_instance(cls, **source)
    except TypeError as e:
        raise TypeError(f"Error at creating {cls.__name__}: {e}")
