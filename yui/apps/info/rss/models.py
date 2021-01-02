from sqlalchemy.schema import Column
from sqlalchemy.types import Integer
from sqlalchemy.types import String

from ....orm import Base
from ....orm.columns import DateTimeAtColumn
from ....orm.columns import DateTimeColumn
from ....orm.columns import TimezoneColumn


class RSSFeedURL(Base):
    """RSS Feed URL"""

    __tablename__ = 'rss_feed_url'

    id = Column(Integer, primary_key=True)

    url = Column(String, nullable=False)

    channel = Column(String, nullable=False)

    updated_datetime = DateTimeColumn(nullable=False)

    updated_timezone = TimezoneColumn()

    updated_at = DateTimeAtColumn('updated')
