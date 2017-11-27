from typing import Any, Dict, List, Mapping, Optional, Union

from .type import (
    Bot,
    Channel,
    ChannelID,
    Comment,
    CommentID,
    DirectMessageChannel,
    DnDStatus,
    File,
    FileID,
    MessageMessage,
    MessagePreviousMessage,
    Namespace,
    PrivateChannel,
    PublicChannel,
    Subteam,
    SubteamID,
    TeamID,
    Ts,
    User,
    UserID,
)

__all__ = (
    'AccountsChanged',
    'BotAdded',
    'BotChanged',
    'ChannelArchive',
    'ChannelCreated',
    'ChannelDeleted',
    'ChannelHistoryChanged',
    'ChannelJoined',
    'ChannelLeft',
    'ChannelMarked',
    'ChannelRename',
    'ChannelUnarchive',
    'DnDUpdated',
    'DnDUpdatedUser',
    'EmailDomainChanged',
    'EmojiChanged',
    'Event',
    'FileChange',
    'FileCommentAdded',
    'FileCommentDeleted',
    'FileCommentEdited',
    'FileCreated',
    'FileDeleted',
    'FilePublic',
    'FileShared',
    'FileUnshared',
    'GoodBye',
    'GroupArchive',
    'GroupClose',
    'GroupHistoryChanged',
    'GroupJoined',
    'GroupLeft',
    'GroupMarked',
    'GroupOpen',
    'GroupRename',
    'GroupUnarchive',
    'Hello',
    'IMClose',
    'IMCreated',
    'IMHistoryChanged',
    'IMMarked',
    'IMOpen',
    'ManualPresenceChange',
    'MemberJoinedChannel',
    'MemberLeftChannel',
    'Message',
    'PinAdded',
    'PinRemoved',
    'PrefChange',
    'PresenceChange',
    'ReactionAdded',
    'ReactionRemoved',
    'ReconnectURL',
    'StarAdded',
    'StarRemoved',
    'SubteamCreated',
    'SubteamMembersChanged',
    'SubteamSelfAdded',
    'SubteamSelfRemoved',
    'SubteamUpdated',
    'TeamDomainChange',
    'TeamJoin',
    'TeamMigrationStarted',
    'TeamPlanChange',
    'TeamPrefChange',
    'TeamProfileChange',
    'TeamProfileDelete',
    'TeamProfileReorder',
    'TeamRename',
    'UserChange',
    'UserTyping',
    'create_event',
)


class Event(Namespace):
    """Event from RTM."""

    type: str
    subtype: Optional[str] = None


class AccountsChanged(Event):
    """The list of accounts a user is signed into has changed."""

    type: str = 'accounts_changed'


class BotAdded(Event):
    """An bot user was added."""

    type: str = 'bot_added'
    bot: Bot


class BotChanged(Event):
    """An bot user was changed."""

    type: str = 'bot_changed'
    bot: Bot


class ChannelArchive(Event):
    """A channel was archived."""

    type: str = 'channel_archive'
    channel: PublicChannel
    user: UserID


class ChannelCreated(Event):
    """A channel was created."""

    type: str = 'channel_created'
    channel: PublicChannel


class ChannelDeleted(Event):
    """A channel was deleted."""

    type: str = 'channel_deleted'
    channel: PublicChannel


class ChannelHistoryChanged(Event):
    """Bulk updates were made to a channel's history."""

    type: str = 'channel_history_changed'
    latest: Ts
    ts: Ts
    event_ts: Ts


class ChannelJoined(Event):
    """You joined a channel."""

    type: str = 'channel_joined'
    channel: PublicChannel


class ChannelLeft(Event):
    """You left a channel."""

    type: str = 'channel_left'
    channel: PublicChannel


class ChannelMarked(Event):
    """Your channel read marker was updated."""

    type: str = 'channel_marked'
    channel: PublicChannel
    ts: Ts


class ChannelRename(Event):
    """A channel was renamed."""

    type: str = 'channel_rename'
    channel: PublicChannel


class ChannelUnarchive(Event):
    """A channel was unarchived."""

    type: str = 'channel_unarchive'
    channel: PublicChannel
    user: UserID


class DnDUpdated(Event):
    """Do not Disturb settings changed for the current user."""

    type: str = 'dnd_updated'
    user: UserID
    dnd_status: DnDStatus


class DnDUpdatedUser(Event):
    """Do not Disturb settings changed for a team member."""

    type: str = 'dnd_updated_user'
    user: UserID
    dnd_status: DnDStatus


class EmailDomainChanged(Event):
    """The team email domain has changed."""

    type: str = 'email_domain_changed'
    email_domain: str
    event_ts: Ts


class EmojiChanged(Event):
    """A team custom emoji has been added or changed."""

    type: str = 'emoji_changed'
    subtype: str
    name: Optional[str]
    names: Optional[List[str]]
    value: Optional[str]
    event_ts: Ts


class FileChange(Event):
    """A file was changed."""

    type: str = 'file_change'
    file_id: FileID
    file: File


class FileCommentAdded(Event):
    """A file comment was added."""

    type: str = 'file_comment_added'
    comment: Comment
    file_id: FileID
    file: File


class FileCommentDeleted(Event):
    """A file comment was deleted."""

    type: str = 'file_comment_deleted'
    comment: CommentID
    file_id: FileID
    file: File


class FileCommentEdited(Event):
    """A file comment was edited."""

    type: str = 'file_comment_edited'
    comment: Comment
    file_id: FileID
    file: File


class FileCreated(Event):
    """A file was created."""

    type: str = 'type_created'
    file_id: FileID
    file: File


class FileDeleted(Event):
    """A file was deleted."""

    type: str = 'file_deleted'
    file_id: FileID
    event_ts: Ts


class FilePublic(Event):
    """A file was made public."""

    type: str = 'file_public'
    file_id: FileID
    file: File


class FileShared(Event):
    """A file was shared."""

    type: str = 'file_shared'
    file_id: FileID
    file: File


class FileUnshared(Event):
    """A file was unshared."""

    type: str = 'file_unshared'
    file_id: FileID
    file: File


class GoodBye(Event):
    """The server intends to close the connection soon."""

    type: str = 'goodbye'


class GroupArchive(Event):
    """A private channel was archived."""

    type: str = 'group_archive'
    channel: PrivateChannel


class GroupClose(Event):
    """You closed a private channel."""

    type: str = 'group_close'
    user: UserID
    channel: PrivateChannel


class GroupHistoryChanged(Event):
    """Bulk updates were made to a private channel's history."""

    type: str = 'group_history_changed'
    latest: Ts
    ts: Ts
    event_ts: Ts


class GroupJoined(Event):
    """You joined a private channel."""

    type: str = 'group_joined'
    channel: PrivateChannel


class GroupLeft(Event):
    """You left a private channel."""

    type: str = 'group_left'
    channel: PrivateChannel


class GroupMarked(Event):
    """A private channel read marker was updated."""

    type: str = 'group_marked'
    channel: PrivateChannel
    ts: Ts


class GroupOpen(Event):
    """You opened a private channel."""

    type: str = 'group_open'
    user: UserID
    channel: PrivateChannel


class GroupRename(Event):
    """A private channel was renamed"""

    type: str = 'group_rename'
    channel: PrivateChannel


class GroupUnarchive(Event):
    """A private channel was unarchived."""

    type: str = 'group_unarchive'
    channel: PrivateChannel


class Hello(Event):
    """The client has successfully connected to the server."""

    type: str = 'hello'


class IMClose(Event):
    """You closed a DM."""

    type: str = 'im_close'
    user: UserID
    channel: DirectMessageChannel


class IMCreated(Event):
    """A DM was created."""

    type: str = 'im_created'
    user: UserID
    channel: DirectMessageChannel


class IMHistoryChanged(Event):
    """Bulk updates were made to a DM's history."""

    type: str = 'im_history_changed'
    latest: Ts
    ts: Ts
    event_ts: Ts


class IMMarked(Event):
    """A direct message read marker was updated."""

    type: str = 'im_marked'
    channel: DirectMessageChannel
    ts: Ts


class IMOpen(Event):
    """You opened a DM."""

    type: str = 'im_open'
    user: UserID
    channel: DirectMessageChannel


class ManualPresenceChange(Event):
    """You manually updated your presence."""

    type: str = 'manualPresence_change'
    presence: str


class MemberJoinedChannel(Event):
    """A user joined a public or private channel."""

    type: str = 'member_joined_channel'
    user: UserID
    channel: Union[PublicChannel, PrivateChannel]
    channel_type: str
    inviter: UserID


class MemberLeftChannel(Event):
    """A user left a public or private channel."""

    type: str = 'member_left_channel'
    user: UserID
    channel: Union[PublicChannel, PrivateChannel]
    channel_type: str


class Message(Event):
    """A message was sent to a channel."""

    type: str = 'message'
    channel: Channel
    user: UserID
    text: str
    ts: Ts
    event_ts: Optional[Ts]
    attachments: Optional[List[Dict[str, Any]]]
    hidden: Optional[bool]
    message: Optional[MessageMessage]
    previous_message: Optional[MessagePreviousMessage]


class PinAdded(Event):
    """A pin was added to a channel."""

    type: str = 'pin_added'
    user: UserID
    channel_id: ChannelID
    item: Mapping
    event_ts: Ts


class PinRemoved(Event):
    """A pin was removed from a channel."""

    type: str = 'pin_added'
    user: UserID
    channel_id: ChannelID
    item: Mapping
    has_pins: bool
    event_ts: Ts


class PrefChange(Event):
    """You have updated your preferences."""

    type: str = 'pref_change'
    name: str
    value: Any


class PresenceChange(Event):
    """A team member's presence changed."""

    type: str = 'presence_change'
    user: Optional[UserID]
    users: Optional[List[UserID]]
    presence: str


class ReactionAdded(Event):
    """A team member has added an emoji reaction to an item."""

    type: str = 'reaction_added'
    user: UserID
    reaction: str
    item_user: UserID
    item: Mapping[str, Any]
    event_ts: Ts


class ReactionRemoved(Event):
    """A team member removed an emoji reaction."""

    type: str = 'reaction_removed'
    user: UserID
    reaction: str
    item_user: UserID
    item: Mapping[str, Any]
    event_ts: Ts


class ReconnectURL(Event):
    """Experimental."""

    type: str = 'reconnect_url'
    url: str


class StarAdded(Event):
    """A team member has starred an item."""

    type: str = 'star_added'
    user: UserID
    item: Mapping
    event_ts: Ts


class StarRemoved(Event):
    """A team member removed a star."""

    type: str = 'star_removed'
    user: UserID
    item: Mapping
    event_ts: Ts


class SubteamCreated(Event):
    """A User Group has been added to the team."""

    type: str = 'subteam_created'
    subteam: Subteam


class SubteamMembersChanged(Event):
    """The membership of an existing User Group has changed."""

    type: str = 'subteam_members_changed'
    subteam_id: SubteamID
    team_id: TeamID
    date_previous_update: int
    date_update: int
    added_users: List[UserID]
    added_users_count: str
    removed_users: List[UserID]
    removed_users_count: str


class SubteamSelfAdded(Event):
    """You have been added to a User Group."""

    type: str = 'subteam_self_added'
    subteam_id = SubteamID


class SubteamSelfRemoved(Event):
    """You have been removed from a User Group."""

    type: str = 'subteam_self_removed'
    subteam_id: SubteamID


class SubteamUpdated(Event):
    """An existing User Group has been updated or its members changed."""

    type: str = 'subteam_updated'
    subteam: Subteam


class TeamDomainChange(Event):
    """The team domain has changed."""

    type: str = 'team_domain_change'
    url: str
    domain: str


class TeamJoin(Event):
    """A new team member has joined."""

    type: str = 'team_join'
    user: User


class TeamMigrationStarted(Event):
    """The team is being migrated between servers."""

    type: str = 'team_migration_started'


class TeamPlanChange(Event):
    """The team billing plan has changed."""

    type: str = 'team_plan_change'
    plan: str


class TeamPrefChange(Event):
    """A team preference has been updated."""

    type: str = 'team_pref_change'
    name: str
    value: Any


class TeamProfileChange(Event):
    """Team profile fields have been updated."""

    type: str = 'team_profile_change'
    profile: Mapping


class TeamProfileDelete(Event):
    """Team profile fields have been deleted."""

    type: str = 'team_profile_delete'
    profile: Mapping


class TeamProfileReorder(Event):
    """Team profile fields have been reordered."""

    type: str = 'team_profile_reorder'
    profile: Mapping


class TeamRename(Event):
    """The team name has changed."""

    type: str = 'team_rename'
    name: str


class UserChange(Event):
    """A team member's data has changed."""

    type: str = 'user_change'
    user: User


class UserTyping(Event):
    """A channel member is typing a message."""

    type: str = 'user_typing'
    channel: Channel
    user: UserID


def create_event(d: Dict) -> Event:
    """Create Event"""

    return {
        cls.type: cls for cls in Event.__subclasses__()
    }.get(d['type'], Event)(**d)
