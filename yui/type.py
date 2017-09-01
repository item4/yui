import inspect

from types import SimpleNamespace

from typing import (
    Any,
    Dict,
    List,
    Mapping,
    MutableSequence,
    NewType,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)

__all__ = (
    'AppID',
    'BotID',
    'Channel',
    'ChannelBase',
    'ChannelID',
    'ChannelPurpose',
    'ChannelTopic',
    'Comment',
    'CommentID',
    'DirectMessageChannel',
    'DirectMessageChannelID',
    'DnDStatus',
    'File',
    'FileID',
    'MessageMessage',
    'MessagePreviousMessage',
    'Namespace',
    'NoneType',
    'PrivateGroupChannel',
    'PrivateGroupChannelID',
    'PublicChannel',
    'PublicChannelID',
    'Subteam',
    'SubteamID',
    'SubteamPrefs',
    'TeamID',
    'Ts',
    'UnionType',
    'UnixTimestamp',
    'UserID',
    'cast',
)

#: :type:`type` User ID type. It must start with 'U'.
UserID = NewType('UserID', str)

#: :type:`type` Public Channel ID type. It must start with 'C'.
PublicChannelID = NewType('PublicChannelID', str)

#: :type:`type` IM(as known as Direct Message) Channel ID type.
#: It must start with 'D'.
DirectMessageChannelID = NewType('DirectMessageChannelID', str)

#: :type:`type` Group(as known as Private Channel) ID type.
#: It must start with 'G'.
PrivateGroupChannelID = NewType('PrivateGroupChannelID', str)

ChannelID = Union[
    PublicChannelID,
    DirectMessageChannelID,
    PrivateGroupChannelID,
]

#: :type:`type` File ID type. It must start with 'F'.
FileID = NewType('FileID', str)

Comment = NewType('Comment', dict)

#: :type:`type` Comment ID type.
CommentID = NewType('CommentID', str)

#: :type:`type` Type for slack event unique ID.
Ts = NewType('Ts', str)

#: :type:`type` Team ID type. It must start with 'T'.
TeamID = NewType('TeamID', str)

#: :type:`type` Sub-team ID type. It must start with 'S'.
SubteamID = NewType('SubteamID', str)

#: :type:`type` App ID type. IT must start with 'A'.
AppID = NewType('AppID', str)

#: :type:`type` Bot ID type. It must start with 'B'.
BotID = NewType('BotID', str)

#: :type:`type` Type for store UnixTimestamp.
UnixTimestamp = NewType('UnixTimestamp', int)


class Namespace(SimpleNamespace):
    """Typed Namespace."""

    def __init__(self, **kwargs) -> None:
        for k, t in self.__annotations__.items():
            kwargs[k] = cast(t, kwargs.get(k))

        super(Namespace, self).__init__(**kwargs)


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


class ChannelBase(Namespace):
    """Channel type base."""

    name: str
    is_channel: bool
    created: UnixTimestamp
    creator: UserID
    is_archived: bool
    is_general: bool
    members: List[UserID]
    topic: ChannelTopic
    purpose: ChannelPurpose
    is_member: bool
    last_read: Ts
    latest: Mapping
    unread_count: int
    unread_count_display: int


class PublicChannel(ChannelBase):
    """
    Public Channel.

    https://api.slack.com/types/channel

    """

    id: PublicChannelID


class DirectMessageChannel(Namespace):
    """
    IM(Direct Message) Channel.

    https://api.slack.com/types/im

    """

    id: DirectMessageChannelID
    is_im: bool
    user: UserID
    created: UnixTimestamp
    is_user_deleted: bool


class PrivateGroupChannel(ChannelBase):
    """
    Private Group Channel.

    https://api.slack.com/types/channel

    """

    id: PrivateGroupChannelID
    is_group: str
    is_mpim: bool


Channel = Union[PublicChannel, DirectMessageChannel, PrivateGroupChannel]


class Bot(Namespace):
    """Bot."""

    id: BotID
    app_id: AppID
    name: str
    icons: Mapping[str, str]


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


class UserProfile(Namespace):
    """Profile of User."""

    avatar_hash: str
    status_emoji: Optional[str]
    status_text: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    real_name: Optional[str]
    email: str
    skype: Optional[str]
    phone: Optional[str]
    image_24: Optional[str]
    image_32: Optional[str]
    image_48: Optional[str]
    image_72: Optional[str]
    image_192: Optional[str]
    image_512: Optional[str]


class User(Namespace):
    """https://api.slack.com/types/user"""

    id: UserID
    name: str
    deleted: bool
    color: str
    profile: UserProfile
    is_admin: bool
    is_owner: bool
    is_primary_owner: bool
    is_restricted: bool
    is_ultra_restricted: bool
    updated: UnixTimestamp
    has_2fa: bool
    two_factor_type: str


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


NoneType = type(None)
UnionType = type(Union)


def cast(t, value):
    """Magical casting."""

    if type(t) == UnionType:
        for ty in t.__args__:
            try:
                return cast(ty, value)
            except:
                continue
        raise ValueError()
    elif t == Any:
        return value
    elif t == NoneType:
        return None
    elif t in (str, bytes):
        return t(value)

    if inspect.isclass(t):
        if issubclass(t, Namespace):
            return t(**value)

        if issubclass(t, Tuple):
            if t.__args__:
                return tuple(cast(ty, x) for ty, x in zip(t.__args__, value))
            else:
                return tuple(value)

        if issubclass(t, Set):
            if t.__args__:
                return {cast(t.__args__[0], x) for x in value}
            else:
                return set(value)

        if issubclass(t, (List, MutableSequence, Sequence)):
            if t.__args__[0]:
                return [cast(t.__args__[0], x) for x in value]
            else:
                return list(value)

        if issubclass(t, (Dict, Mapping)):
            if t.__args__:
                return {
                    cast(t.__args__[0], k): cast(t.__args__[1], v)
                    for k, v in value.items()
                }
            else:
                return dict(value)

    return t(value)
