from datetime import datetime

from sqlalchemy.orm import Mapped

from ....orm import Base
from ....orm.types import PrimaryKey


class RSSFeedURL(Base):
    """RSS Feed URL"""

    __tablename__ = "rss_feed_url"

    id: Mapped[PrimaryKey]

    url: Mapped[str]

    channel: Mapped[str]

    updated_at: Mapped[datetime]
