from .base import Ts
from .base import UserID
from ..utils.attrs import define
from ..utils.attrs import field
from ..utils.attrs import ts_field
from ..utils.attrs import user_id_field


@define
class MessageMessageEdited:
    """edited attr in MessageMessage."""

    user: UserID = user_id_field()
    ts: Ts = ts_field()


@define
class MessageMessage:
    """Message in Message."""

    user: UserID = user_id_field()
    ts: Ts = ts_field()
    type: str = field()
    text: str = field()
    edited: MessageMessageEdited | None = field(repr=True)
