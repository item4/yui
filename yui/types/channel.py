from datetime import datetime

from ..utils.attrs import channel_id_field
from ..utils.attrs import define
from ..utils.attrs import field
from ..utils.attrs import name_field
from ..utils.attrs import ts_field
from ..utils.attrs import user_id_field
from .base import DirectMessageChannelID
from .base import PrivateChannelID
from .base import PublicChannelID
from .base import Ts
from .base import UserID


@define
class ChannelTopic:
    """Topic of Channel."""

    creator: UserID = user_id_field()
    value: str = field()
    last_set: datetime = field()


@define
class ChannelPurpose:
    """Purpose of Channel."""

    creator: UserID = user_id_field()
    value: str = field()
    last_set: datetime = field()


@define
class PublicChannel:

    id: PublicChannelID = channel_id_field()
    name: str = name_field()
    is_channel: bool = field()
    is_group: bool = field()
    is_im: bool = field()
    created: datetime = field()
    creator: UserID = user_id_field()
    is_archived: bool = field()
    is_general: bool = field()
    unlinked: int = field()
    name_normalized: str = field()
    is_read_only: bool = field()
    is_shared: bool = field()
    parent_conversation: object = field()
    is_ext_shared: bool = field()
    is_org_shared: bool = field()
    is_pending_ext_shared: bool = field()
    is_member: bool = field()
    is_private: bool = field()
    is_mpim: bool = field()
    last_read: Ts = ts_field()
    topic: ChannelTopic = field()
    purpose: ChannelPurpose = field()
    locale: str = field()


@define
class DirectMessageChannel:

    id: DirectMessageChannelID = channel_id_field()
    created: datetime = field()
    is_im: bool = field()
    is_org_shared: bool = field()
    user: UserID = user_id_field()
    last_read: Ts = ts_field()
    latest: object = field()
    unread_count: int = field()
    unread_count_display: int = field()
    is_open: bool = field()
    locale: str = field()
    priority: float = field()
    num_members: int = field()


@define
class PrivateChannel:

    id: PrivateChannelID = channel_id_field()
    name: str = field()
    is_channel: bool = field()
    is_group: bool = field()
    is_im: bool = field()
    created: datetime = field()
    creator: UserID = user_id_field()
    is_archived: bool = field()
    is_general: bool = field()
    unlinked: int = field()
    name_normalized: str = field()
    is_read_only: bool = field()
    is_shared: bool = field()
    parent_conversation: object = field()
    is_ext_shared: bool = field()
    is_org_shared: bool = field()
    is_pending_ext_shared: bool = field()
    is_member: bool = field()
    is_private: bool = field()
    is_mpim: bool = field()
    last_read: Ts = ts_field()
    topic: ChannelTopic = field()
    purpose: ChannelPurpose = field()
    locale: str = field()
