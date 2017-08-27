from decimal import Decimal

from typing import List, Mapping, NewType, Optional, Sequence, Type, Union

from mypy_extensions import TypedDict

__all__ = (
    'AppID',
    'BotID',
    'Channel',
    'ChannelBase',
    'ChannelID',
    'Comment',
    'CommentID',
    'DirectMessageChannel',
    'DirectMessageChannelID',
    'DnDStatus',
    'File',
    'FileID',
    'PrivateGroupChannel',
    'PrivateGroupChannelID',
    'PublicChannel',
    'PublicChannelID',
    'Subteam',
    'SubteamID',
    'TeamID',
    'Ts',
    'UnixTimestamp',
    'UserID',
    'decimal_range',
    'float_range',
    'int_range',
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


class ChannelBase(TypedDict, total=False):
    """Channel type base."""

    name: str
    is_channel: bool
    created: UnixTimestamp
    creator: UserID
    is_archived: bool
    is_general: bool
    members: List[UserID]
    topic: TypedDict(
        'Topic',
        {
            'value': str,
            'creator': UserID,
            'last_set': UnixTimestamp,
        },
        total=False,
    )
    purpose: TypedDict(
        'Purpose',
        {
            'value': str,
            'creator': UserID,
            'last_set': UnixTimestamp,
        },
        total=False,
    )
    is_member: bool
    last_read: Ts
    latest: Mapping
    unread_count: int
    unread_count_display: int


class PublicChannel(ChannelBase, total=False):
    """
    Public Channel.

    https://api.slack.com/types/channel

    """

    id: PublicChannelID


class DirectMessageChannel(TypedDict, total=False):
    """
    IM(Direct Message) Channel.

    https://api.slack.com/types/im

    """

    id: DirectMessageChannelID
    is_im: bool
    user: UserID
    created: UnixTimestamp
    is_user_deleted: bool


class PrivateGroupChannel(ChannelBase, total=False):
    """
    Private Group Channel.

    https://api.slack.com/types/channel

    """

    id: PrivateGroupChannelID
    is_group: str
    is_mpim: bool


Channel = Union[PublicChannel, DirectMessageChannel, PrivateGroupChannel]


class Bot(TypedDict, total=False):
    """Bot."""

    id: BotID
    app_id: AppID
    name: str
    icons: Mapping[str, str]


class DnDStatus(TypedDict, total=False):
    """DnD status."""

    dnd_enabled: bool
    next_dnd_start_ts: UnixTimestamp
    next_dnd_end_ts: UnixTimestamp
    snooze_enabled: Optional[bool]
    snooze_endtime: Optional[UnixTimestamp]


class File(TypedDict, total=False):
    """https://api.slack.com/types/file"""

    id: FileID


class User(TypedDict, total=False):
    """https://api.slack.com/types/user"""

    id: UserID
    name: str
    deleted: bool
    color: str
    profile: TypedDict('Profile', {
        'avatar_hash': str,
        'status_emoji': str,
        'status_text': str,
        'first_name': Optional[str],
        'last_name': Optional[str],
        'real_name': Optional[str],
        'email': str,
        'skype': Optional[str],
        'phone': Optional[str],
        'image_24': Optional[str],
        'image_32': Optional[str],
        'image_48': Optional[str],
        'image_72': Optional[str],
        'image_192': Optional[str],
        'image_512': Optional[str],
    }, total=False)
    is_admin: bool
    is_owner: bool
    is_primary_owner: bool
    is_restricted: bool
    is_ultra_restricted: bool
    updated: UnixTimestamp
    has_2fa: bool
    two_factor_type: str


class Subteam(TypedDict, total=False):
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
    perfs: TypedDict('Prefs', {
        'channels': List,
        'groups': List,
    }, total=False)
    users: List[UserID]
    user_count: str


def choice(
    cases: Sequence[str],
    *,
    fallback: Optional[str]=None,
    case_insensitive: bool=False
) -> Type[str]:
    """Helper for constraint input value must be in cases."""

    class _Str(str):

        def __new__(cls, *args, **kwargs) -> str:  # type: ignore
            snew = super(_Str, cls).__new__
            val = snew(cls, *args, **kwargs)  # type: ignore

            if case_insensitive:
                if val.lower() in map(lambda x: x.lower(), cases):
                    return val
                else:
                    if fallback is not None:
                        return fallback
                    else:
                        raise ValueError('given value is not in allowed cases')
            else:
                if val in cases:
                    return val
                else:
                    if fallback is not None:
                        return fallback
                    else:
                        raise ValueError('given value is not in allowed cases')

    return _Str


def decimal_range(
    start: Decimal,
    end: Decimal,
    *,
    autofix: bool=False
) -> Type[Decimal]:
    """Helper for constraint range of decimal value."""

    class _Decimal(Decimal):

        def __new__(cls, *args, **kwargs) -> Decimal:  # type: ignore
            snew = super(_Decimal, cls).__new__
            val = snew(cls, *args, **kwargs)  # type: ignore

            if start <= val <= end:
                return val
            elif start > val:
                if autofix:
                    return start
                else:
                    raise ValueError('given value is too small.')
            else:
                if autofix:
                    return end
                else:
                    raise ValueError('given value is too big.')

    return _Decimal


def float_range(
    start: float,
    end: float,
    *,
    autofix: bool=False
) -> Type[float]:
    """Helper for constraint range of floating point number value."""

    class _Float(float):

        def __new__(cls, *args, **kwargs) -> float:  # type: ignore
            snew = super(_Float, cls).__new__
            val = snew(cls, *args, **kwargs)  # type: ignore

            if start <= val <= end:
                return val
            elif start > val:
                if autofix:
                    return start
                else:
                    raise ValueError('given value is too small.')
            else:
                if autofix:
                    return end
                else:
                    raise ValueError('given value is too big.')

    return _Float


def int_range(start: int, end: int, *, autofix: bool=False) -> Type[int]:
    """Helper for constraint range of integer value."""

    class _Int(int):

        def __new__(cls, *args, **kwargs) -> int:  # type: ignore
            snew = super(_Int, cls).__new__
            val = snew(cls, *args, **kwargs)  # type: ignore

            if start <= val <= end:
                return val
            elif start > val:
                if autofix:
                    return start
                else:
                    raise ValueError('given value is too small.')
            else:
                if autofix:
                    return end
                else:
                    raise ValueError('given value is too big.')

    return _Int
