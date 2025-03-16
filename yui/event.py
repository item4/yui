from typing import Any
from typing import ClassVar
from typing import Literal
from typing import NoReturn
from typing import overload

from attrs import define

from .types.base import ChannelID
from .types.base import Ts
from .types.base import UserID
from .types.objects import MessageMessage
from .utils.attrs import channel_id_field
from .utils.attrs import field
from .utils.attrs import field_transformer
from .utils.attrs import make_instance
from .utils.attrs import ts_field
from .utils.attrs import user_id_field

type GoodByeType = Literal["goodbye"]
type HelloType = Literal["hello"]
type MessageType = Literal["message"]
type PongType = Literal["pong"]
type TeamJoinType = Literal["team_join"]
type TeamMigrationStartedType = Literal["team_migration_started"]
type YuiSystemStartType = Literal["yui_system_start"]

type EventType = Literal[
    GoodByeType,
    HelloType,
    MessageType,
    PongType,
    TeamJoinType,
    TeamMigrationStartedType,
    YuiSystemStartType,
]
type Source = dict[str, Any]


class EventBase:
    """Base class of Event."""


class Event(EventBase):
    """Base class of knwon event."""

    type: ClassVar[str]
    subtype: str | None


_events: dict[EventType, type[Event]] = {}


def event(cls):
    _events[cls.type] = cls
    return cls


@define(kw_only=True, field_transformer=field_transformer)
class UnknownEvent(EventBase):
    """Unknown Event."""

    type: str
    kwargs: dict[str, Any]


@event
@define(kw_only=True, field_transformer=field_transformer)
class GoodBye(Event):
    """The server intends to close the connection soon."""

    type: ClassVar[str] = "goodbye"


@event
@define(kw_only=True, field_transformer=field_transformer)
class Hello(Event):
    """The client has successfully connected to the server."""

    type: ClassVar[str] = "hello"


@event
@define(kw_only=True, field_transformer=field_transformer)
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
@define(kw_only=True, field_transformer=field_transformer)
class Pong(Event):
    """Ping-Pong"""

    type: ClassVar[str] = "pong"


@event
@define(kw_only=True, field_transformer=field_transformer)
class TeamJoin(Event):
    """A new team member has joined."""

    type: ClassVar[str] = "team_join"
    user: UserID = user_id_field()


@event
@define(kw_only=True, field_transformer=field_transformer)
class TeamMigrationStarted(Event):
    """The team is being migrated between servers."""

    type: ClassVar[str] = "team_migration_started"


@event
@define(kw_only=True, field_transformer=field_transformer)
class YuiSystemStart(Event):
    """System event for start system."""

    type: ClassVar[str] = "yui_system_start"


@overload
def create_event(type_: GoodByeType, source: Source) -> GoodBye: ...  # type: ignore[overload-overlap]


@overload
def create_event(type_: HelloType, source: Source) -> Hello: ...  # type: ignore[overload-overlap]


@overload
def create_event(type_: MessageType, source: Source) -> Message: ...  # type: ignore[overload-overlap]


@overload
def create_event(type_: PongType, source: Source) -> Pong: ...  # type: ignore[overload-overlap]


@overload
def create_event(type_: TeamJoinType, source: Source) -> TeamJoin: ...  # type: ignore[overload-overlap]


@overload
def create_event(  # type: ignore[overload-overlap]
    type_: TeamMigrationStartedType,
    source: Source,
) -> TeamMigrationStarted: ...


@overload
def create_event(  # type: ignore[overload-overlap]
    type_: YuiSystemStartType,
    source: Source,
) -> YuiSystemStart: ...


@overload
def create_event(
    type_: str,
    source: Source,
) -> NoReturn: ...


def create_event(type_, source):
    """Create Event"""

    try:
        cls = _events[type_]
    except KeyError as e:
        error = f"Unknwon event type: {type_}"
        raise TypeError(error) from e

    try:
        return make_instance(cls, **source)
    except TypeError as e:
        error = f"Error at creating {cls.__name__}: {e}"
        raise TypeError(error) from e


def create_unknown_event(type_: str, source: Source) -> UnknownEvent:
    return UnknownEvent(type=type_, kwargs=source)
