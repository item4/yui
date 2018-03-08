from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime, Integer, String, Text

from .type import JSONType
from ..orm import Base


class WebPageCache(Base):
    """Cache for web page"""

    __tablename__ = 'web_page_cache'

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False, unique=True)

    body = Column(Text)

    created_at = Column(DateTime(timezone=True), nullable=False)


class JSONCache(Base):

    __tablename__ = 'json_cache'

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False, unique=True)

    body = Column(JSONType)

    created_at = Column(DateTime(timezone=True), nullable=False)
