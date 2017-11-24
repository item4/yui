from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime, Integer, String, Text

from ..orm import Base


class RssFeedSub(Base):
    """RSS Feed Subscribe"""

    __tablename__ = 'feed'

    id = Column(Integer, primary_key=True)

    url = Column(String, nullable=False)

    channel = Column(String, nullable=False)

    updated_at = Column(DateTime(timezone=True), nullable=False)


class SiteSub(Base):
    """Site diff Subscribe"""

    __tablename__ = 'site_sub'

    id = Column(Integer, primary_key=True)

    url = Column(String, nullable=False)

    user = Column(String(10), nullable=False)

    body = Column(Text)
