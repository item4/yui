from typing import Any
from typing import ClassVar
from typing import Dict
from typing import List
from typing import Optional
from typing import Type
from typing import Union

from .types.base import ChannelID
from .types.base import Comment
from .types.base import CommentID
from .types.base import FileID
from .types.base import SubteamID
from .types.base import TeamID
from .types.base import Ts
from .types.channel import Channel
from .types.channel import DirectMessageChannel
from .types.channel import PrivateChannel
from .types.channel import PublicChannel
from .types.namespace import BooleanField
from .types.namespace import ChannelField
from .types.namespace import Field
from .types.namespace import IDField
from .types.namespace import IntegerField
from .types.namespace import ListField
from .types.namespace import OptionalField
from .types.namespace import StringField
from .types.namespace import TsField
from .types.namespace import UserField
from .types.namespace import UserListField
from .types.namespace import namespace
from .types.objects import BotObject
from .types.objects import DnDStatus
from .types.objects import File
from .types.objects import MessageMessage
from .types.objects import MessagePreviousMessage
from .types.objects import Subteam
from .types.user import User


class BaseEvent:
    """Base class of Event."""


class Event(BaseEvent):
    """Event."""

    type: ClassVar[str]
    subtype: Optional[str] = None


_events: Dict[str, Type[BaseEvent]] = {}


def event(cls):
    cls = namespace(cls)
    _events[cls.type] = cls
    return cls


@namespace
class UnknownEvent(BaseEvent):
    """Unknown Event."""


@event
class AccountsChanged(Event):
    """The list of accounts a user is signed into has changed."""

    type: ClassVar[str] = 'accounts_changed'


@event
class BotAdded(Event):
    """An bot user was added."""

    type: ClassVar[str] = 'bot_added'
    bot: BotObject = Field(converter=BotObject)


@event
class BotChanged(Event):
    """An bot user was changed."""

    type: ClassVar[str] = 'bot_changed'
    bot: BotObject = Field(converter=BotObject)


@event
class ChannelArchive(Event):
    """A channel was archived."""

    type: ClassVar[str] = 'channel_archive'
    channel: PublicChannel = ChannelField()
    user: User = UserField()


@event
class ChannelCreated(Event):
    """A channel was created."""

    type: ClassVar[str] = 'channel_created'
    channel: PublicChannel = ChannelField()


@event
class ChannelDeleted(Event):
    """A channel was deleted."""

    type: ClassVar[str] = 'channel_deleted'
    channel: PublicChannel = ChannelField()


@event
class ChannelHistoryChanged(Event):
    """Bulk updates were made to a channel's history."""

    type: ClassVar[str] = 'channel_history_changed'
    latest: Ts = TsField()
    ts: Ts = TsField()
    event_ts: Ts = TsField()


@event
class ChannelJoined(Event):
    """You joined a channel."""

    type: ClassVar[str] = 'channel_joined'
    channel: PublicChannel = ChannelField()


@event
class ChannelLeft(Event):
    """You left a channel."""

    type: ClassVar[str] = 'channel_left'
    channel: PublicChannel = ChannelField()


@event
class ChannelMarked(Event):
    """Your channel read marker was updated."""

    type: ClassVar[str] = 'channel_marked'
    channel: PublicChannel = ChannelField()
    ts: Ts = TsField()


@event
class ChannelRename(Event):
    """A channel was renamed."""

    type: ClassVar[str] = 'channel_rename'
    channel: PublicChannel = ChannelField()


@event
class ChannelUnarchive(Event):
    """A channel was unarchived."""

    type: ClassVar[str] = 'channel_unarchive'
    channel: PublicChannel = ChannelField()
    user: User = UserField()


@event
class DnDUpdated(Event):
    """Do not Disturb settings changed for the current user."""

    type: ClassVar[str] = 'dnd_updated'
    user: User = UserField()
    dnd_status: DnDStatus = Field(converter=DnDStatus)


@event
class DnDUpdatedUser(Event):
    """Do not Disturb settings changed for a team member."""

    type: ClassVar[str] = 'dnd_updated_user'
    user: User = UserField()
    dnd_status: DnDStatus = Field(converter=DnDStatus)


@event
class EmailDomainChanged(Event):
    """The team email domain has changed."""

    type: ClassVar[str] = 'email_domain_changed'
    event_ts: Ts = TsField()
    email_domain: str = StringField()


@event
class EmojiChanged(Event):
    """A team custom emoji has been added or changed."""

    type: ClassVar[str] = 'emoji_changed'
    event_ts: Ts = TsField()
    name: str = StringField()
    names: List[str] = ListField(str)()
    value: str = StringField()


@event
class FileChange(Event):
    """A file was changed."""

    type: ClassVar[str] = 'file_change'
    file_id: FileID = IDField()
    file: File = Field(converter=File)


@event
class FileCommentAdded(Event):
    """A file comment was added."""

    type: ClassVar[str] = 'file_comment_added'
    file_id: FileID = IDField()
    comment: Comment = Field(converter=Comment)
    file: File = Field(converter=File)


@event
class FileCommentDeleted(Event):
    """A file comment was deleted."""

    type: ClassVar[str] = 'file_comment_deleted'
    comment: CommentID = IDField()
    file_id: FileID = IDField()
    file: File = Field(converter=File)


@event
class FileCommentEdited(Event):
    """A file comment was edited."""

    type: ClassVar[str] = 'file_comment_edited'
    file_id: FileID = IDField()
    comment: Comment = Field(converter=Comment)
    file: File = Field(converter=File)


@event
class FileCreated(Event):
    """A file was created."""

    type: ClassVar[str] = 'type_created'
    file_id: FileID = IDField()
    file: File = Field(converter=File)


@event
class FileDeleted(Event):
    """A file was deleted."""

    type: ClassVar[str] = 'file_deleted'
    file_id: FileID = IDField()
    event_ts: Ts = TsField()


@event
class FilePublic(Event):
    """A file was made public."""

    type: ClassVar[str] = 'file_public'
    file_id: FileID = IDField()
    file: File = Field(converter=File)


@event
class FileShared(Event):
    """A file was shared."""

    type: ClassVar[str] = 'file_shared'
    file_id: FileID = IDField()
    file: File = Field(converter=File)


@event
class FileUnshared(Event):
    """A file was unshared."""

    type: ClassVar[str] = 'file_unshared'
    file_id: FileID = IDField()
    file: File = Field(converter=File)


@event
class GoodBye(Event):
    """The server intends to close the connection soon."""

    type: ClassVar[str] = 'goodbye'


@event
class GroupArchive(Event):
    """A private channel was archived."""

    type: ClassVar[str] = 'group_archive'
    channel: PrivateChannel = ChannelField()


@event
class GroupClose(Event):
    """You closed a private channel."""

    type: ClassVar[str] = 'group_close'
    user: User = UserField()
    channel: PrivateChannel = ChannelField()


@event
class GroupHistoryChanged(Event):
    """Bulk updates were made to a private channel's history."""

    type: ClassVar[str] = 'group_history_changed'
    latest: Ts = TsField()
    ts: Ts = TsField()
    event_ts: Ts = TsField()


@event
class GroupJoined(Event):
    """You joined a private channel."""

    type: ClassVar[str] = 'group_joined'
    channel: PrivateChannel = ChannelField()


@event
class GroupLeft(Event):
    """You left a private channel."""

    type: ClassVar[str] = 'group_left'
    channel: PrivateChannel = ChannelField()


@event
class GroupMarked(Event):
    """A private channel read marker was updated."""

    type: ClassVar[str] = 'group_marked'
    channel: PrivateChannel = ChannelField()
    ts: Ts = TsField()


@event
class GroupOpen(Event):
    """You opened a private channel."""

    type: ClassVar[str] = 'group_open'
    user: User = UserField()
    channel: PrivateChannel = ChannelField()


@event
class GroupRename(Event):
    """A private channel was renamed"""

    type: ClassVar[str] = 'group_rename'
    channel: PrivateChannel = ChannelField()


@event
class GroupUnarchive(Event):
    """A private channel was unarchived."""

    type: ClassVar[str] = 'group_unarchive'
    channel: PrivateChannel = ChannelField()


@event
class Hello(Event):
    """The client has successfully connected to the server."""

    type: ClassVar[str] = 'hello'


@event
class IMClose(Event):
    """You closed a DM."""

    type: ClassVar[str] = 'im_close'
    user: User = UserField()
    channel: DirectMessageChannel = ChannelField()


@event
class IMCreated(Event):
    """A DM was created."""

    type: ClassVar[str] = 'im_created'
    user: User = UserField()
    channel: DirectMessageChannel = ChannelField()


@event
class IMHistoryChanged(Event):
    """Bulk updates were made to a DM's history."""

    type: ClassVar[str] = 'im_history_changed'
    latest: Ts = TsField()
    ts: Ts = TsField()
    event_ts: Ts = TsField()


@event
class IMMarked(Event):
    """A direct message read marker was updated."""

    type: ClassVar[str] = 'im_marked'
    channel: DirectMessageChannel = ChannelField()
    ts: Ts = TsField()


@event
class IMOpen(Event):
    """You opened a DM."""

    type: ClassVar[str] = 'im_open'
    user: User = UserField()
    channel: DirectMessageChannel = ChannelField()


@event
class ManualPresenceChange(Event):
    """You manually updated your presence."""

    type: ClassVar[str] = 'manual_presence_change'
    presence: str = StringField()


@event
class MemberJoinedChannel(Event):
    """A user joined a public or private channel."""

    type: ClassVar[str] = 'member_joined_channel'
    user: User = UserField()
    channel: Union[PublicChannel, PrivateChannel] = ChannelField()
    inviter: User = UserField()
    channel_type: str = StringField()


@event
class MemberLeftChannel(Event):
    """A user left a public or private channel."""

    type: ClassVar[str] = 'member_left_channel'
    user: User = UserField()
    channel: Union[PublicChannel, PrivateChannel] = ChannelField()
    channel_type: str = StringField()


@event
class Message(Event):
    """A message was sent to a channel."""

    type: ClassVar[str] = 'message'
    channel: Channel = ChannelField()
    ts: Ts = TsField(repr=True)
    event_ts: Ts = TsField()
    user: User = UserField(default=None)
    text: str = StringField(repr=True)
    attachments: List[Dict[str, Any]] = Field()
    hidden: bool = BooleanField()
    message: MessageMessage = OptionalField(MessageMessage)(repr=True)
    previous_message: MessagePreviousMessage = OptionalField(
        MessagePreviousMessage
    )(repr=True)
    subtype: Optional[str] = OptionalField(str)(repr=True)


@event
class PinAdded(Event):
    """A pin was added to a channel."""

    type: ClassVar[str] = 'pin_added'
    user: User = UserField()
    channel_id: ChannelID = IDField()
    event_ts: Ts = TsField()
    item: Dict = Field()


@event
class PinRemoved(Event):
    """A pin was removed from a channel."""

    type: ClassVar[str] = 'pin_added'
    user: User = UserField()
    channel_id: ChannelID = IDField()
    event_ts: Ts = TsField()
    item: Dict = Field()
    has_pins: bool = BooleanField()


@event
class Pong(BaseEvent):
    """Ping-Pong"""

    type: ClassVar[str] = 'pong'


@event
class PrefChange(Event):
    """You have updated your preferences."""

    type: ClassVar[str] = 'pref_change'
    name: str = StringField()
    value: Any = Field()


@event
class PresenceChange(Event):
    """A team member's presence changed."""

    type: ClassVar[str] = 'presence_change'
    user: User = UserField()
    users: List[User] = UserListField()
    presence: str = StringField()


@event
class ReactionAdded(Event):
    """A team member has added an emoji reaction to an item."""

    type: ClassVar[str] = 'reaction_added'
    user: User = UserField()
    item_user: User = UserField()
    event_ts: Ts = TsField()
    reaction: str = StringField()
    item: Dict[str, Any] = Field()


@event
class ReactionRemoved(Event):
    """A team member removed an emoji reaction."""

    type: ClassVar[str] = 'reaction_removed'
    item_user: User = UserField()
    user: User = UserField()
    event_ts: Ts = TsField()
    reaction: str = StringField()
    item: Dict[str, Any] = Field()


@event
class ReconnectURL(Event):
    """Experimental."""

    type: ClassVar[str] = 'reconnect_url'
    url: str = StringField()


@event
class StarAdded(Event):
    """A team member has starred an item."""

    type: ClassVar[str] = 'star_added'
    user: User = UserField()
    event_ts: Ts = TsField()
    item: Dict = Field()


@event
class StarRemoved(Event):
    """A team member removed a star."""

    type: ClassVar[str] = 'star_removed'
    user: User = UserField()
    event_ts: Ts = TsField()
    item: Dict = Field()


@event
class SubteamCreated(Event):
    """A User Group has been added to the team."""

    type: ClassVar[str] = 'subteam_created'
    subteam: Subteam = Field(converter=Subteam)


@event
class SubteamMembersChanged(Event):
    """The membership of an existing User Group has changed."""

    type: ClassVar[str] = 'subteam_members_changed'
    subteam_id: SubteamID = IDField()
    team_id: TeamID = IDField()
    date_previous_update: int = IntegerField()
    date_update: int = IntegerField()
    added_users: List[User] = UserListField()
    added_users_count: str = StringField()
    removed_users: List[User] = UserListField()
    removed_users_count: str = StringField()


@event
class SubteamSelfAdded(Event):
    """You have been added to a User Group."""

    type: ClassVar[str] = 'subteam_self_added'
    subteam_id: SubteamID = IDField()


@event
class SubteamSelfRemoved(Event):
    """You have been removed from a User Group."""

    type: ClassVar[str] = 'subteam_self_removed'
    subteam_id: SubteamID = IDField()


@event
class SubteamUpdated(Event):
    """An existing User Group has been updated or its members changed."""

    type: ClassVar[str] = 'subteam_updated'
    subteam: Subteam = Field(converter=Subteam)


@event
class TeamDomainChange(Event):
    """The team domain has changed."""

    type: ClassVar[str] = 'team_domain_change'
    url: str = StringField()
    domain: str = StringField()


@event
class TeamJoin(Event):
    """A new team member has joined."""

    type: ClassVar[str] = 'team_join'
    user: User = UserField()


@event
class TeamMigrationStarted(Event):
    """The team is being migrated between servers."""

    type: ClassVar[str] = 'team_migration_started'


@event
class TeamPlanChange(Event):
    """The team billing plan has changed."""

    type: ClassVar[str] = 'team_plan_change'
    plan: str = StringField()


@event
class TeamPrefChange(Event):
    """A team preference has been updated."""

    type: ClassVar[str] = 'team_pref_change'
    name: str = StringField()
    value: Any = Field()


@event
class TeamProfileChange(Event):
    """Team profile fields have been updated."""

    type: ClassVar[str] = 'team_profile_change'
    profile: Dict = Field()


@event
class TeamProfileDelete(Event):
    """Team profile fields have been deleted."""

    type: ClassVar[str] = 'team_profile_delete'
    profile: Dict = Field()


@event
class TeamProfileReorder(Event):
    """Team profile fields have been reordered."""

    type: ClassVar[str] = 'team_profile_reorder'
    profile: Dict = Field()


@event
class TeamRename(Event):
    """The team name has changed."""

    type: ClassVar[str] = 'team_rename'
    name: str = StringField()


@event
class UserChange(Event):
    """A team member's data has changed."""

    type: ClassVar[str] = 'user_change'
    user: User = UserField()


@event
class UserTyping(Event):
    """A channel member is typing a message."""

    type: ClassVar[str] = 'user_typing'
    channel: Channel = ChannelField()
    user: User = UserField()


@event
class ChatterboxSystemStart(Event):
    """System event for start system."""

    type: ClassVar[str] = 'chatterbox_system_start'


def create_event(d: Dict) -> BaseEvent:
    """Create Event"""

    cls = _events.get(d['type'])
    if cls:
        d.pop('type')
    else:
        cls = UnknownEvent
    try:
        return cls(**d)  # type: ignore
    except TypeError as e:
        raise TypeError(f'Error at creating {cls.__name__}: {e}')
