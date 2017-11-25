from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime, Integer, String, Text

from ..orm import Base
from ..util import tz_none_to_kst, tz_none_to_utc


class WebPageCache(Base):
    """Cache for web page"""

    __tablename__ = 'web_page_cache'

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False, unique=True)

    body = Column(Text)

    created_datetime = Column(DateTime(timezone=True), nullable=False)

    @hybrid_property
    def created_at(self):

        return tz_none_to_kst(self.created_datetime)

    @created_at.setter
    def created_at_setter(self, value):

        self.created_datetime = tz_none_to_utc(value)
