from datetime import datetime
from typing import List

from .base import Ts
from .namespace import (
    BooleanField,
    DateTimeField,
    Field,
    IDField,
    IntegerField,
    ListField,
    NameField,
    StringField,
    TsField,
    UserField,
    UserListField,
    namespace,
)
from .user import User


@namespace
class ChannelTopic:
    """Topic of Channel."""

    creator: User = UserField()
    value: str = StringField()
    last_set: datetime = DateTimeField()


@namespace
class ChannelPurpose:
    """Purpose of Channel."""

    creator: User = UserField()
    value: str = StringField()
    last_set: datetime = DateTimeField()


@namespace
class Channel:

    id: str = IDField()
    last_read: Ts = TsField()
    created: datetime = DateTimeField()
    is_org_shared: bool = BooleanField()
    has_pins: bool = BooleanField()
    is_unknown: bool = BooleanField(init=False, repr=True, default=False)


@namespace
class PublicChannel(Channel):

    id: str = IDField()
    name: str = NameField()
    creator: User = UserField()
    last_read: Ts = TsField()
    members: List[User] = UserListField()
    created: datetime = DateTimeField()
    is_org_shared: bool = BooleanField()
    has_pins: bool = BooleanField()
    is_channel: bool = BooleanField()
    is_archived: bool = BooleanField()
    is_general: bool = BooleanField()
    unlinked: int = IntegerField()
    name_normalized: str = StringField()
    is_shared: bool = BooleanField()
    is_member: bool = BooleanField()
    is_private: bool = BooleanField()
    is_mpim: bool = BooleanField()
    topic: ChannelTopic = Field(converter=ChannelTopic)
    purpose: ChannelPurpose = Field(converter=ChannelPurpose)
    previous_names: List[str] = ListField(str)()


@namespace
class DirectMessageChannel(Channel):

    id: str = IDField()
    user: User = UserField()
    last_read: Ts = TsField()
    is_im: bool = BooleanField()
    created: datetime = DateTimeField()
    is_org_shared: bool = BooleanField()
    has_pins: bool = BooleanField()
    is_open: bool = BooleanField()


@namespace
class PrivateChannel(Channel):

    id: str = IDField()
    name: str = NameField()
    creator: User = UserField()
    last_read: Ts = TsField()
    members: List[User] = UserListField()
    created: datetime = DateTimeField()
    is_org_shared: bool = BooleanField()
    has_pins: bool = BooleanField()
    is_group: bool = BooleanField()
    is_archived: bool = BooleanField()
    topic: ChannelTopic = Field(converter=ChannelTopic)
    purpose: ChannelPurpose = Field(converter=ChannelPurpose)


def create_unknown_channel(**kwargs):
    if 'last_read' not in kwargs:
        kwargs['last_read'] = ''
    channel = Channel(**kwargs)
    channel.is_unknown = True
    return channel
