from typing import Dict, List, TYPE_CHECKING, Union
from typing import cast as typing_cast

from .base import Namespace
from .objects import ChannelPurpose, ChannelTopic, UserProfile
from ..base import TeamID, Ts, UnixTimestamp, UserID
from ...exceptions import AllChannelsError, NoChannelsError

if TYPE_CHECKING:
    from ...bot import Bot


class BotLinkedNamespace(Namespace):
    """Bot-linked namespace."""

    _bot: 'Bot'


class FromID(BotLinkedNamespace):
    """.from_id"""

    @classmethod
    def from_id(cls, value: Union[str, Dict]):
        raise NotImplementedError()


class FromChannelID(FromID):
    """.from_id"""

    @classmethod
    def from_id(cls, value: Union[str, Dict], raise_error: bool = False):
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
        channel_name = cls._bot.config.CHANNELS[key]
        if isinstance(channel_name, str):
            return cls.from_name(channel_name)
        raise ValueError(f'{key} in CHANNELS is not str.')

    @classmethod
    def from_config_list(cls, key: str)\
            -> List[Union['PrivateChannel', 'PublicChannel']]:
        channels = cls._bot.config.CHANNELS[key]
        if not channels:
            raise NoChannelsError()
        if channels == ['*'] or channels == '*':
            raise AllChannelsError()
        if isinstance(channels, list):
            return [cls.from_name(x) for x in channels]
        raise ValueError(f'{key} in CHANNELS is not list.')


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
    user: UserID
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
    def from_id(cls, value: Union[str, Dict], raise_error: bool = False):
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
