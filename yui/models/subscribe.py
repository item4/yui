from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, Text

from .util import insert_datetime_field
from ..orm import Base


class RssFeedSub(Base):
    """RSS Feed Subscribe"""

    __tablename__ = 'feed'

    id = Column(Integer, primary_key=True)

    url = Column(String, nullable=False)

    channel = Column(String, nullable=False)

    insert_datetime_field('updated', locals(), False)


class SiteSub(Base):
    """Site diff Subscribe"""

    __tablename__ = 'site_sub'

    id = Column(Integer, primary_key=True)

    url = Column(String, nullable=False)

    user = Column(String, nullable=False)

    body = Column(Text)
