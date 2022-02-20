from typing import Any
from typing import ClassVar
from typing import Literal
from typing import NoReturn
from typing import Optional
from typing import Type
from typing import Union
from typing import overload

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
from .types.objects import Subteam
from .types.user import User


AccountsChangedType = Literal['accounts_changed']
BotAddedType = Literal['bot_added']
BotChangedType = Literal['bot_changed']
ChannelArchiveType = Literal['channel_archive']
ChannelCreatedType = Literal['channel_created']
ChannelDeletedType = Literal['channel_deleted']
ChannelHistoryChangedType = Literal['channel_history_changed']
ChannelJoinedType = Literal['channel_joined']
ChannelLeftType = Literal['channel_left']
ChannelMarkedType = Literal['channel_marked']
ChannelRenameType = Literal['channel_rename']
ChannelUnarchiveType = Literal['channel_unarchive']
DnDUpdatedType = Literal['dnd_updated']
DnDUpdatedUserType = Literal['dnd_updated_user']
EmailDomainChangedType = Literal['email_domain_changed']
EmojiChangedType = Literal['emoji_changed']
FileChangeType = Literal['file_change']
FileCommentAddedType = Literal['file_comment_added']
FileCommentDeletedType = Literal['file_comment_deleted']
FileCommentEditedType = Literal['file_comment_edited']
FileCreatedType = Literal['type_created']
FileDeletedType = Literal['file_deleted']
FilePublicType = Literal['file_public']
FileSharedType = Literal['file_shared']
FileUnsharedType = Literal['file_unshared']
GoodByeType = Literal['goodbye']
GroupArchiveType = Literal['group_archive']
GroupCloseType = Literal['group_close']
GroupHistoryChangedType = Literal['group_history_changed']
GroupJoinedType = Literal['group_joined']
GroupLeftType = Literal['group_left']
GroupMarkedType = Literal['group_marked']
GroupOpenType = Literal['group_open']
GroupRenameType = Literal['group_rename']
GroupUnarchiveType = Literal['group_unarchive']
HelloType = Literal['hello']
IMCloseType = Literal['im_close']
IMCreatedType = Literal['im_created']
IMHistoryChangedType = Literal['im_history_changed']
IMMarkedType = Literal['im_marked']
IMOpenType = Literal['im_open']
ManualPresenceChangeType = Literal['manual_presence_change']
MemberJoinedChannelType = Literal['member_joined_channel']
MemberLeftChannelType = Literal['member_left_channel']
MessageType = Literal['message']
PinRemovedType = Literal['pin_added']
PongType = Literal['pong']
PrefChangeType = Literal['pref_change']
PresenceChangeType = Literal['presence_change']
ReactionAddedType = Literal['reaction_added']
ReactionRemovedType = Literal['reaction_removed']
ReconnectURLType = Literal['reconnect_url']
StarAddedType = Literal['star_added']
StarRemovedType = Literal['star_removed']
SubteamCreatedType = Literal['subteam_created']
SubteamMembersChangedType = Literal['subteam_members_changed']
SubteamSelfAddedType = Literal['subteam_self_added']
SubteamSelfRemovedType = Literal['subteam_self_removed']
SubteamUpdatedType = Literal['subteam_updated']
TeamDomainChangeType = Literal['team_domain_change']
TeamJoinType = Literal['team_join']
TeamMigrationStartedType = Literal['team_migration_started']
TeamPlanChangeType = Literal['team_plan_change']
TeamPrefChangeType = Literal['team_pref_change']
TeamProfileChangeType = Literal['team_profile_change']
TeamProfileDeleteType = Literal['team_profile_delete']
TeamProfileReorderType = Literal['team_profile_reorder']
TeamRenameType = Literal['team_rename']
UserChangeType = Literal['user_change']
UserTypingType = Literal['user_typing']
YuiSystemStartType = Literal['yui_system_start']

EventType = Literal[
    AccountsChangedType,
    BotAddedType,
    BotChangedType,
    ChannelArchiveType,
    ChannelCreatedType,
    ChannelDeletedType,
    ChannelHistoryChangedType,
    ChannelJoinedType,
    ChannelLeftType,
    ChannelMarkedType,
    ChannelRenameType,
    ChannelUnarchiveType,
    DnDUpdatedType,
    DnDUpdatedUserType,
    EmailDomainChangedType,
    EmojiChangedType,
    FileChangeType,
    FileCommentAddedType,
    FileCommentDeletedType,
    FileCommentEditedType,
    FileCreatedType,
    FileDeletedType,
    FilePublicType,
    FileSharedType,
    FileUnsharedType,
    GoodByeType,
    GroupArchiveType,
    GroupCloseType,
    GroupHistoryChangedType,
    GroupJoinedType,
    GroupLeftType,
    GroupMarkedType,
    GroupOpenType,
    GroupRenameType,
    GroupUnarchiveType,
    HelloType,
    IMCloseType,
    IMCreatedType,
    IMHistoryChangedType,
    IMMarkedType,
    IMOpenType,
    ManualPresenceChangeType,
    MemberJoinedChannelType,
    MemberLeftChannelType,
    MessageType,
    PinRemovedType,
    PongType,
    PrefChangeType,
    PresenceChangeType,
    ReactionAddedType,
    ReactionRemovedType,
    ReconnectURLType,
    StarAddedType,
    StarRemovedType,
    SubteamCreatedType,
    SubteamMembersChangedType,
    SubteamSelfAddedType,
    SubteamSelfRemovedType,
    SubteamUpdatedType,
    TeamDomainChangeType,
    TeamJoinType,
    TeamMigrationStartedType,
    TeamPlanChangeType,
    TeamPrefChangeType,
    TeamProfileChangeType,
    TeamProfileDeleteType,
    TeamProfileReorderType,
    TeamRenameType,
    UserChangeType,
    UserTypingType,
    YuiSystemStartType,
]
Source = dict[str, Any]


class BaseEvent:
    """Base class of Event."""


class Event(BaseEvent):
    """Event."""

    type: ClassVar[str]
    subtype: Optional[str] = None


_events: dict[EventType, Type[BaseEvent]] = {}


def event(cls):
    cls = namespace(cls)
    _events[cls.type] = cls
    return cls


@namespace
class UnknownEvent(BaseEvent):
    """Unknown Event."""

    type: str


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
    names: list[str] = ListField(str)()
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
    attachments: list[dict[str, Any]] = Field()
    hidden: bool = BooleanField()
    message: MessageMessage = OptionalField(MessageMessage)(repr=True)
    subtype: Optional[str] = OptionalField(str)(repr=True)


@event
class PinAdded(Event):
    """A pin was added to a channel."""

    type: ClassVar[str] = 'pin_added'
    user: User = UserField()
    channel_id: ChannelID = IDField()
    event_ts: Ts = TsField()
    item: dict = Field()


@event
class PinRemoved(Event):
    """A pin was removed from a channel."""

    type: ClassVar[str] = 'pin_added'
    user: User = UserField()
    channel_id: ChannelID = IDField()
    event_ts: Ts = TsField()
    item: dict = Field()
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
    users: list[User] = UserListField()
    presence: str = StringField()


@event
class ReactionAdded(Event):
    """A team member has added an emoji reaction to an item."""

    type: ClassVar[str] = 'reaction_added'
    user: User = UserField()
    item_user: User = UserField()
    event_ts: Ts = TsField()
    reaction: str = StringField()
    item: dict[str, Any] = Field()


@event
class ReactionRemoved(Event):
    """A team member removed an emoji reaction."""

    type: ClassVar[str] = 'reaction_removed'
    item_user: User = UserField()
    user: User = UserField()
    event_ts: Ts = TsField()
    reaction: str = StringField()
    item: dict[str, Any] = Field()


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
    item: dict = Field()


@event
class StarRemoved(Event):
    """A team member removed a star."""

    type: ClassVar[str] = 'star_removed'
    user: User = UserField()
    event_ts: Ts = TsField()
    item: dict = Field()


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
    added_users: list[User] = UserListField()
    added_users_count: str = StringField()
    removed_users: list[User] = UserListField()
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
    profile: dict = Field()


@event
class TeamProfileDelete(Event):
    """Team profile fields have been deleted."""

    type: ClassVar[str] = 'team_profile_delete'
    profile: dict = Field()


@event
class TeamProfileReorder(Event):
    """Team profile fields have been reordered."""

    type: ClassVar[str] = 'team_profile_reorder'
    profile: dict = Field()


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
class YuiSystemStart(Event):
    """System event for start system."""

    type: ClassVar[str] = 'yui_system_start'


@overload
def create_event(
    type_: AccountsChangedType, source: Source
) -> AccountsChanged:
    ...


@overload
def create_event(type_: BotAddedType, source: Source) -> BotAdded:
    ...


@overload
def create_event(type_: BotChangedType, source: Source) -> BotChanged:
    ...


@overload
def create_event(type_: ChannelArchiveType, source: Source) -> ChannelArchive:
    ...


@overload
def create_event(type_: ChannelCreatedType, source: Source) -> ChannelCreated:
    ...


@overload
def create_event(type_: ChannelDeletedType, source: Source) -> ChannelDeleted:
    ...


@overload
def create_event(
    type_: ChannelHistoryChangedType, source: Source
) -> ChannelHistoryChanged:
    ...


@overload
def create_event(type_: ChannelJoinedType, source: Source) -> ChannelJoined:
    ...


@overload
def create_event(type_: ChannelLeftType, source: Source) -> ChannelLeft:
    ...


@overload
def create_event(type_: ChannelMarkedType, source: Source) -> ChannelMarked:
    ...


@overload
def create_event(type_: ChannelRenameType, source: Source) -> ChannelRename:
    ...


@overload
def create_event(
    type_: ChannelUnarchiveType, source: Source
) -> ChannelUnarchive:
    ...


@overload
def create_event(type_: DnDUpdatedType, source: Source) -> DnDUpdated:
    ...


@overload
def create_event(type_: DnDUpdatedUserType, source: Source) -> DnDUpdatedUser:
    ...


@overload
def create_event(
    type_: EmailDomainChangedType, source: Source
) -> EmailDomainChanged:
    ...


@overload
def create_event(type_: EmojiChangedType, source: Source) -> EmojiChanged:
    ...


@overload
def create_event(type_: FileChangeType, source: Source) -> FileChange:
    ...


@overload
def create_event(
    type_: FileCommentAddedType, source: Source
) -> FileCommentAdded:
    ...


@overload
def create_event(
    type_: FileCommentDeletedType, source: Source
) -> FileCommentDeleted:
    ...


@overload
def create_event(
    type_: FileCommentEditedType, source: Source
) -> FileCommentEdited:
    ...


@overload
def create_event(type_: FileCreatedType, source: Source) -> FileCreated:
    ...


@overload
def create_event(type_: FileDeletedType, source: Source) -> FileDeleted:
    ...


@overload
def create_event(type_: FilePublicType, source: Source) -> FilePublic:
    ...


@overload
def create_event(type_: FileSharedType, source: Source) -> FileShared:
    ...


@overload
def create_event(type_: FileUnsharedType, source: Source) -> FileUnshared:
    ...


@overload
def create_event(type_: GoodByeType, source: Source) -> GoodBye:
    ...


@overload
def create_event(type_: GroupArchiveType, source: Source) -> GroupArchive:
    ...


@overload
def create_event(type_: GroupCloseType, source: Source) -> GroupClose:
    ...


@overload
def create_event(
    type_: GroupHistoryChangedType, source: Source
) -> GroupHistoryChanged:
    ...


@overload
def create_event(type_: GroupJoinedType, source: Source) -> GroupJoined:
    ...


@overload
def create_event(type_: GroupLeftType, source: Source) -> GroupLeft:
    ...


@overload
def create_event(type_: GroupMarkedType, source: Source) -> GroupMarked:
    ...


@overload
def create_event(type_: GroupOpenType, source: Source) -> GroupOpen:
    ...


@overload
def create_event(type_: GroupRenameType, source: Source) -> GroupRename:
    ...


@overload
def create_event(type_: GroupUnarchiveType, source: Source) -> GroupUnarchive:
    ...


@overload
def create_event(type_: HelloType, source: Source) -> Hello:
    ...


@overload
def create_event(type_: IMCloseType, source: Source) -> IMClose:
    ...


@overload
def create_event(type_: IMCreatedType, source: Source) -> IMCreated:
    ...


@overload
def create_event(
    type_: IMHistoryChangedType, source: Source
) -> IMHistoryChanged:
    ...


@overload
def create_event(type_: IMMarkedType, source: Source) -> IMMarked:
    ...


@overload
def create_event(type_: IMOpenType, source: Source) -> IMOpen:
    ...


@overload
def create_event(
    type_: ManualPresenceChangeType, source: Source
) -> ManualPresenceChange:
    ...


@overload
def create_event(
    type_: MemberJoinedChannelType, source: Source
) -> MemberJoinedChannel:
    ...


@overload
def create_event(
    type_: MemberLeftChannelType, source: Source
) -> MemberLeftChannel:
    ...


@overload
def create_event(type_: MessageType, source: Source) -> Message:
    ...


@overload
def create_event(type_: PinRemovedType, source: Source) -> PinRemoved:
    ...


@overload
def create_event(type_: PongType, source: Source) -> Pong:
    ...


@overload
def create_event(type_: PrefChangeType, source: Source) -> PrefChange:
    ...


@overload
def create_event(type_: PresenceChangeType, source: Source) -> PresenceChange:
    ...


@overload
def create_event(type_: ReactionAddedType, source: Source) -> ReactionAdded:
    ...


@overload
def create_event(
    type_: ReactionRemovedType, source: Source
) -> ReactionRemoved:
    ...


@overload
def create_event(type_: ReconnectURLType, source: Source) -> ReconnectURL:
    ...


@overload
def create_event(type_: StarAddedType, source: Source) -> StarAdded:
    ...


@overload
def create_event(type_: StarRemovedType, source: Source) -> StarRemoved:
    ...


@overload
def create_event(type_: SubteamCreatedType, source: Source) -> SubteamCreated:
    ...


@overload
def create_event(
    type_: SubteamMembersChangedType, source: Source
) -> SubteamMembersChanged:
    ...


@overload
def create_event(
    type_: SubteamSelfAddedType, source: Source
) -> SubteamSelfAdded:
    ...


@overload
def create_event(
    type_: SubteamSelfRemovedType, source: Source
) -> SubteamSelfRemoved:
    ...


@overload
def create_event(type_: SubteamUpdatedType, source: Source) -> SubteamUpdated:
    ...


@overload
def create_event(
    type_: TeamDomainChangeType, source: Source
) -> TeamDomainChange:
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
def create_event(type_: TeamPlanChangeType, source: Source) -> TeamPlanChange:
    ...


@overload
def create_event(type_: TeamPrefChangeType, source: Source) -> TeamPrefChange:
    ...


@overload
def create_event(
    type_: TeamProfileChangeType, source: Source
) -> TeamProfileChange:
    ...


@overload
def create_event(
    type_: TeamProfileDeleteType, source: Source
) -> TeamProfileDelete:
    ...


@overload
def create_event(
    type_: TeamProfileReorderType, source: Source
) -> TeamProfileReorder:
    ...


@overload
def create_event(type_: TeamRenameType, source: Source) -> TeamRename:
    ...


@overload
def create_event(type_: UserChangeType, source: Source) -> UserChange:
    ...


@overload
def create_event(type_: UserTypingType, source: Source) -> UserTyping:
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
