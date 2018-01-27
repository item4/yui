from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime, Integer, String, Text

from ..orm import Base
from ..util import tz_none_to_kst, tz_none_to_utc


class Memo(Base):
    """Memo"""

    __tablename__ = 'memo'

    id = Column(Integer, primary_key=True)

    keyword = Column(String, nullable=False)

    text = Column(Text, nullable=False)

    author = Column(String, nullable=False)

    created_datetime = Column(DateTime(timezone=True), nullable=False)

    @hybrid_property
    def created_at(self):

        return tz_none_to_kst(self.created_datetime)

    @created_at.setter  # type: ignore
    def created_at(self, value):

        self.created_datetime = tz_none_to_utc(value)
