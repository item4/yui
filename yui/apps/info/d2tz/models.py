from datetime import datetime

from sqlalchemy.orm import Mapped
from sqlalchemy.schema import UniqueConstraint

from ....orm import Base
from ....orm.types import PrimaryKey
from .commons import tz_id_to_names


class TerrorZoneLog(Base):
    """TerrorZone Log"""

    __tablename__ = "terrorzonelog"

    id: Mapped[PrimaryKey]

    levels: Mapped[list[int]]

    start_at: Mapped[datetime]

    fetched_at: Mapped[datetime]

    broadcasted_at: Mapped[datetime | None]

    next_fetch_at: Mapped[datetime]

    __table_args__ = (UniqueConstraint("start_at"),)

    def to_slack_text(self, /) -> str:
        tz_names = ", ".join(tz_id_to_names(self.levels))
        fallback_dt = self.start_at.strftime("%Y-%m-%d %H:%M")
        return f"[<!date^{int(self.start_at.timestamp())}^{{date_num}} {{time}}|{fallback_dt}>] {tz_names}"

    def to_discord_text(self, /) -> str:
        tz_names = ", ".join(tz_id_to_names(self.levels))
        return f"<t:{int(self.start_at.timestamp())}:f>: {tz_names}"
