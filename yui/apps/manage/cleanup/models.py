from sqlalchemy.orm import Mapped
from sqlalchemy.schema import UniqueConstraint

from ....orm import Base
from ....orm.types import PrimaryKey


class EventLog(Base):
    """EventLog for cleanup function"""

    __tablename__ = "event_log"

    id: Mapped[PrimaryKey]

    ts: Mapped[str]

    channel: Mapped[str]

    __table_args__ = (UniqueConstraint("ts", "channel"),)
