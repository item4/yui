from typing import Dict, List, Optional

from .base import Namespace
from ..base import (
    AppID,
    BotID,
    FileID,
    SubteamID,
    TeamID,
    Ts,
    UnixTimestamp,
    UserID,
)


class ChannelTopic(Namespace):
    """Topic of Channel."""

    value: str
    creator: UserID
    last_set: UnixTimestamp


class ChannelPurpose(Namespace):
    """Purpose of Channel."""

    value: str
    creator: UserID
    last_set: UnixTimestamp


class UserProfile(Namespace):
    """Profile of User."""

    first_name: str
    last_name: str
    avatar_hash: str
    title: str
    real_name: str
    display_name: str
    real_name_normalized: str
    display_name_normalized: str
    email: str
    image_24: str
    image_32: str
    image_48: str
    image_72: str
    image_192: str
    image_512: str
    team: TeamID


class BotObject(Namespace):
    """Bot."""

    id: BotID
    app_id: AppID
    name: str
    icons: Dict[str, str]


class DnDStatus(Namespace):
    """DnD status."""

    dnd_enabled: bool
    next_dnd_start_ts: UnixTimestamp
    next_dnd_end_ts: UnixTimestamp
    snooze_enabled: Optional[bool]
    snooze_endtime: Optional[UnixTimestamp]


class File(Namespace):
    """https://api.slack.com/types/file"""

    id: FileID


class SubteamPrefs(Namespace):
    """Prefs of Subteam."""

    channels: List
    groups: List


class Subteam(Namespace):
    """https://api.slack.com/types/usergroup"""

    id: SubteamID
    team_id: TeamID
    is_usergroup: bool
    name: str
    description: str
    handle: str
    is_external: bool
    date_create: UnixTimestamp
    date_update: UnixTimestamp
    date_delete: UnixTimestamp
    auto_type: str
    created_by: UserID
    updated_by: Optional[UserID]
    deleted_by: Optional[UserID]
    perfs: SubteamPrefs
    users: List[UserID]
    user_count: str


class MessageMessageEdited(Namespace):
    """edited attr in MessageMessage."""

    user: UserID
    ts: Ts


class MessageMessage(Namespace):
    """Message in Message."""

    type: str
    text: str
    user: UserID
    ts: Ts
    edited: Optional[MessageMessageEdited]


class MessagePreviousMessage(MessageMessage):
    """Previous message in Message."""
