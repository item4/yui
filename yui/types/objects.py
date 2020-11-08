from datetime import datetime
from typing import Optional

from .base import AppID
from .base import BotID
from .base import FileID
from .base import SubteamID
from .base import TeamID
from .base import Ts
from .namespace import BooleanField
from .namespace import ChannelListField
from .namespace import DateTimeField
from .namespace import Field
from .namespace import IDField
from .namespace import NameField
from .namespace import OptionalField
from .namespace import OptionalUserField
from .namespace import StringField
from .namespace import TsField
from .namespace import UserField
from .namespace import UserListField
from .namespace import namespace
from .user import User


@namespace
class BotObject:
    """Bot."""

    id: BotID = IDField()
    app_id: AppID = IDField()
    name: str = NameField()
    icons: dict[str, str] = Field()


@namespace
class DnDStatus:
    """DnD status."""

    dnd_enabled: bool = BooleanField()
    next_dnd_start_ts: datetime = DateTimeField()
    next_dnd_end_ts: datetime = DateTimeField()
    snooze_enabled: bool = BooleanField()
    snooze_endtime: datetime = DateTimeField()


@namespace
class File:
    """https://api.slack.com/types/file"""

    id: FileID = IDField()


@namespace
class SubteamPrefs:
    """Prefs of Subteam."""

    channels: list = ChannelListField()
    groups: list = ChannelListField()


@namespace
class Subteam:
    """https://api.slack.com/types/usergroup"""

    id: SubteamID = IDField()
    team_id: TeamID = IDField()
    name: str = NameField()
    created_by: User = UserField()
    is_usergroup: bool = BooleanField()
    description: str = StringField()
    handle: str = StringField()
    is_external: bool = BooleanField()
    date_create: datetime = DateTimeField()
    date_update: datetime = DateTimeField()
    date_delete: datetime = DateTimeField()
    auto_type: str = StringField()
    updated_by: Optional[User] = OptionalUserField()
    deleted_by: Optional[User] = OptionalUserField()
    perfs: SubteamPrefs = Field(converter=SubteamPrefs)
    users: list[User] = UserListField()
    user_count: str = StringField()


@namespace
class MessageMessageEdited:
    """edited attr in MessageMessage."""

    user: User = UserField()
    ts: Ts = TsField()


@namespace
class MessageMessage:
    """Message in Message."""

    user: User = UserField()
    ts: Ts = TsField()
    type: str = StringField()
    text: str = StringField()
    edited: Optional[MessageMessageEdited] = OptionalField(
        MessageMessageEdited
    )()


@namespace
class MessagePreviousMessage(MessageMessage):
    """Previous message in Message."""
