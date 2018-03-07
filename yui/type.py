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
    TYPE_CHECKING,
    Union,
    cast as typing_cast,
)

if TYPE_CHECKING:
    from .bot import Bot as _Bot  # noqa

__all__ = (
    'AppID',
    'Bot',
    'BotID',
    'BotLinkedNamespace',
    'Channel',
    'ChannelFromConfig',
    'ChannelsFromConfig',
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
    'FromChannelID',
    'FromID',
    'FromUserID',
    'MessageMessage',
    'MessageMessageEdited',
    'MessagePreviousMessage',
    'Namespace',
    'PrivateChannel',
    'PrivateChannelID',
    'PublicChannel',
    'PublicChannelID',
    'Subteam',
    'SubteamID',
    'SubteamPrefs',
    'TeamID',
    'Ts',
    'UnixTimestamp',
    'UnknownChannel',
    'UnknownUser',
    'User',
    'UserID',
    'UserProfile',
    'cast',
    'is_container',
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
PrivateChannelID = NewType('PrivateChannelID', str)

ChannelID = Union[
    PublicChannelID,
    DirectMessageChannelID,
    PrivateChannelID,
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
        annotations = getattr(self, '__annotations__', {})
        for k, v in kwargs.items():
            t = annotations.get(k)
            if t:
                kwargs[k] = cast(t, v)

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


class BotLinkedNamespace(Namespace):
    """Bot-linked namespace."""

    _bot: '_Bot' = None


class FromID(BotLinkedNamespace):
    """.from_id"""

    @classmethod
    def from_id(cls, value: Union[str, Dict]):
        raise NotImplementedError()


class FromChannelID(FromID):
    """.from_id"""

    @classmethod
    def from_id(cls, value: Union[str, Dict], raise_error: bool=False):
        if isinstance(value, str):
            if value.startswith('C'):
                for c in cls._bot.channels:
                    if c.id == value:
                        return c
            elif value.startswith('D'):
                for d in cls._bot.ims:
                    if d.id == value:
                        return d
            elif value.startswith('G'):
                for g in cls._bot.groups:
                    if g.id == value:
                        return g
            if not raise_error:
                return UnknownChannel(id=value)
            raise KeyError('Given ID was not found.')
        return cls(**value)

    @classmethod
    def from_name(cls, name: str):
        for c in cls._bot.channels:
            if c.name == name:
                return c
        for g in cls._bot.groups:
            if g.name == name:
                return g
        raise KeyError('Channel was not found')

    @classmethod
    def from_config(cls, key: str)\
            -> Union['PrivateChannel', 'PublicChannel']:
        return cls.from_name(cls._bot.config.CHANNELS[key])

    @classmethod
    def from_config_list(cls, key: str)\
            -> List[Union['PrivateChannel', 'PublicChannel']]:
        return [cls.from_name(x) for x in cls._bot.config.CHANNELS[key]]


class Channel(FromChannelID):

    id: str
    created: UnixTimestamp
    is_org_shared: bool
    has_pins: bool
    last_read: Ts


class PublicChannel(Channel):

    name: str
    is_channel: bool
    is_archived: bool
    is_general: bool
    unlinked: int
    creator: UserID
    name_normalized: str
    is_shared: bool
    is_member: bool
    is_private: bool
    is_mpim: bool
    members: List[UserID]
    topic: ChannelTopic
    purpose: ChannelPurpose
    previous_names: List[str]

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(id={self.id!r}, name={self.name!r})'


class DirectMessageChannel(Channel):

    is_im: bool
    user: UserID = None
    last_read: Ts
    is_open: bool

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(id={self.id!r}, user={self.user!r})'


class PrivateChannel(Channel):

    name: str
    is_group: bool
    creator: UserID
    is_archived: bool
    members: List[UserID]
    topic: ChannelTopic
    purpose: ChannelPurpose

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(id={self.id!r}, name={self.name!r})'


class UnknownChannel(Channel):
    pass


class ChannelFromConfig:
    """Lazy loading helper to get channel from config"""

    def __init__(self, key: str) -> None:
        self.key = key

    def get(self) -> Union[PrivateChannel, PublicChannel]:
        return Channel.from_config(self.key)


class ChannelsFromConfig:
    """Lazy loading helper to get list of channels from config"""

    def __init__(self, key: str) -> None:
        self.key = key

    def get(self) -> List[Union[PrivateChannel, PublicChannel]]:
        return Channel.from_config_list(self.key)


class FromUserID(FromID):

    @classmethod
    def from_id(cls, value: Union[str, Dict], raise_error: bool=False):
        if isinstance(value, str):
            value = typing_cast(UserID, value)
            if value.startswith('U') and value in cls._bot.users:
                return cls._bot.users[value]
            if not raise_error:
                return UnknownUser(id=value)
            raise KeyError('Given ID was not found.')
        return cls(**value)

    @classmethod
    def from_name(cls, name: str):
        for c in cls._bot.users.values():
            if c.name == name:
                return c
        raise KeyError('Channel was not found')


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


class User(FromUserID):

    id: str
    team_id: TeamID
    name: str
    deleted: bool
    color: str
    real_name: str
    tz: str
    tz_label: str
    tz_offset: int
    profile: UserProfile
    is_admin: bool
    is_owner: bool
    is_primary_owner: bool
    is_restricted: bool
    is_ultra_restricted: bool
    is_bot: bool
    updated: UnixTimestamp
    is_app_user: bool
    has_2fa: bool
    locale: str
    presence: str

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(id={self.id!r}, name={self.name!r})'


class UnknownUser(FromUserID):

    id: str

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(id={self.id!r})'


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
            except:  # noqa: E722
                continue
        raise ValueError()
    elif t == Any:
        return value
    elif t == NoneType:
        return None
    elif t in (str, bytes):
        return t(value)

    if inspect.isclass(t):
        if issubclass(t, FromID):
            return t.from_id(value)

        if issubclass(t, Namespace):
            return t(**value)

        if issubclass(t, tuple):
            if t.__args__:
                return tuple(cast(ty, x) for ty, x in zip(t.__args__, value))
            else:
                return tuple(value)

        if issubclass(t, set):
            if t.__args__:
                return {cast(t.__args__[0], x) for x in value}
            else:
                return set(value)

        if issubclass(t, (list, MutableSequence, Sequence)):
            if t.__args__:
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


def is_container(t) -> bool:
    """Check given value is container type?"""

    return any(issubclass(t, x) for x in [set, tuple, list])
