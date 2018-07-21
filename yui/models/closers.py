from sqlalchemy.schema import Column
from sqlalchemy.types import Date, Integer, String

from .util import insert_datetime_field
from ..orm import Base


class Notice(Base):
    """Notice."""

    __tablename__ = 'closers_notice'

    article_sn = Column(Integer, nullable=False, primary_key=True)

    category = Column(String, nullable=False)

    title = Column(String, nullable=False)

    posted_date = Column(Date, nullable=False)

    insert_datetime_field('updated', locals(), False)


class Event(Base):
    """Event"""

    __tablename__ = 'closers_event'

    article_sn = Column(Integer, nullable=False, primary_key=True)

    title = Column(String, nullable=False)

    posted_date = Column(Date, nullable=False)


class GMNote(Base):
    """GM Note"""

    __tablename__ = 'closers_gm_note'

    article_sn = Column(Integer, nullable=False, primary_key=True)

    title = Column(String, nullable=False)

    text = Column(String, nullable=False)

    image_url = Column(String, nullable=False)

    posted_date = Column(Date, nullable=False)
