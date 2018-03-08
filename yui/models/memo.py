from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime, Integer, String, Text

from ..orm import Base


class Memo(Base):
    """Memo"""

    __tablename__ = 'memo'

    id = Column(Integer, primary_key=True)

    keyword = Column(String, nullable=False)

    text = Column(Text, nullable=False)

    author = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), nullable=False)
