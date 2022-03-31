from datetime import datetime

from ..utils.attrs import define
from ..utils.attrs import field
from ..utils.attrs import name_field
from ..utils.attrs import user_id_field


@define
class UserProfile:
    """Profile of User."""

    first_name: str = field()
    last_name: str = field()
    avatar_hash: str = field()
    title: str = field()
    real_name: str = field()
    display_name: str = field()
    real_name_normalized: str = field(repr=True)
    display_name_normalized: str = field()
    email: str = field()
    image_24: str = field()
    image_32: str = field()
    image_48: str = field()
    image_72: str = field()
    image_192: str = field()
    image_512: str = field()


@define
class User:

    id: str = user_id_field()
    name: str = name_field()
    deleted: bool = field()
    color: str = field()
    real_name: str = field()
    tz: str = field()
    tz_label: str = field()
    tz_offset: int = field()
    profile: UserProfile = field()
    is_admin: bool = field()
    is_owner: bool = field()
    is_primary_owner: bool = field()
    is_restricted: bool = field()
    is_ultra_restricted: bool = field()
    is_bot: bool = field()
    updated: datetime = field()
    is_app_user: bool = field()
    has_2fa: bool = field()
    locale: str = field()
    presence: str = field()
    is_unknown: bool = field(init=False, repr=True, default=False)


def create_unknown_user(**kwargs):
    if "name" not in kwargs:
        kwargs["name"] = ""
    user = User(**kwargs)
    user.is_unknown = True
    return user
