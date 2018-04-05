from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, Text

from .util import insert_datetime_field
from ..orm import Base


class Memo(Base):
    """Memo"""

    __tablename__ = 'memo'

    id = Column(Integer, primary_key=True)

    keyword = Column(String, nullable=False)

    text = Column(Text, nullable=False)

    author = Column(String, nullable=False)

    insert_datetime_field('created', locals(), False)
