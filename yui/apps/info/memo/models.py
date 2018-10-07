from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, Text

from ....orm import Base
from ....orm.util import insert_datetime_field


class Memo(Base):
    """Memo"""

    __tablename__ = 'memo'

    id = Column(Integer, primary_key=True)

    keyword = Column(String, nullable=False)

    text = Column(Text, nullable=False)

    author = Column(String, nullable=False)

    insert_datetime_field('created', locals(), False)
