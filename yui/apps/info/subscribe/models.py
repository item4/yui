from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String

from ....orm import Base
from ....orm.util import insert_datetime_field


class RSSFeedURL(Base):
    """RSS Feed URL to subscribe"""

    __tablename__ = 'rss_feed_url'

    id = Column(Integer, primary_key=True)

    url = Column(String, nullable=False)

    channel = Column(String, nullable=False)

    insert_datetime_field('updated', locals(), False)
