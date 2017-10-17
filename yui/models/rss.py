from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime, Integer, String

from ..orm import Base


class Feed(Base):
    """Feed"""

    __tablename__ = 'feed'

    id = Column(Integer, primary_key=True)

    url = Column(String, nullable=False)

    channel = Column(String, nullable=False)

    updated_at = Column(DateTime(timezone=True), nullable=False)
