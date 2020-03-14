from datetime import datetime

from .base import TeamID
from .namespace import BooleanField
from .namespace import DateTimeField
from .namespace import Field
from .namespace import IDField
from .namespace import NameField
from .namespace import StringField
from .namespace import namespace


@namespace
class UserProfile:
    """Profile of User."""

    team: TeamID = IDField()
    first_name: str = StringField()
    last_name: str = StringField()
    avatar_hash: str = StringField()
    title: str = StringField()
    real_name: str = StringField()
    display_name: str = StringField()
    real_name_normalized: str = StringField()
    display_name_normalized: str = StringField()
    email: str = StringField()
    image_24: str = StringField()
    image_32: str = StringField()
    image_48: str = StringField()
    image_72: str = StringField()
    image_192: str = StringField()
    image_512: str = StringField()


@namespace
class User:

    id: str = IDField()
    name: str = NameField()
    team_id: TeamID = IDField()
    deleted: bool = BooleanField()
    color: str = StringField()
    real_name: str = StringField()
    tz: str = StringField()
    tz_label: str = StringField()
    tz_offset: int = StringField()
    profile: UserProfile = Field(converter=UserProfile)
    is_admin: bool = BooleanField()
    is_owner: bool = BooleanField()
    is_primary_owner: bool = BooleanField()
    is_restricted: bool = BooleanField()
    is_ultra_restricted: bool = BooleanField()
    is_bot: bool = BooleanField()
    updated: datetime = DateTimeField()
    is_app_user: bool = BooleanField()
    has_2fa: bool = BooleanField()
    locale: str = StringField()
    presence: str = StringField()
    is_unknown: bool = BooleanField(init=False, repr=True, default=False)


def create_unknown_user(**kwargs):
    if 'name' not in kwargs:
        kwargs['name'] = ''
    if 'team_id' not in kwargs:
        kwargs['team_id'] = ''
    user = User(**kwargs)
    user.is_unknown = True
    return user
