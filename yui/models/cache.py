from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, Text

from .type import JSONType
from .util import insert_datetime_field
from ..orm import Base


class WebPageCache(Base):
    """Cache for web page"""

    __tablename__ = 'web_page_cache'

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False, unique=True)

    body = Column(Text)

    insert_datetime_field('created', locals(), False)


class JSONCache(Base):

    __tablename__ = 'json_cache'

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False, unique=True)

    body = Column(JSONType)

    insert_datetime_field('created', locals(), False)
