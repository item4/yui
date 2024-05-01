from attrs import define

from ..utils.attrs import field
from ..utils.attrs import field_transformer
from ..utils.attrs import ts_field
from ..utils.attrs import user_id_field
from .base import Ts
from .base import UserID


@define(kw_only=True, field_transformer=field_transformer)
class MessageMessageEdited:
    """edited attr in MessageMessage."""

    user: UserID = user_id_field()
    ts: Ts = ts_field()


@define(kw_only=True, field_transformer=field_transformer)
class MessageMessage:
    """Message in Message."""

    user: UserID = user_id_field()
    ts: Ts = ts_field()
    type: str = field()
    text: str = field()
    edited: MessageMessageEdited | None = field(repr=True)
