from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, Text

from ....orm import Base
from ....orm.utils import insert_datetime_field

__all__ = (
    'Memo',
)


class Memo(Base):
    """Memo"""

    __tablename__ = 'memo'

    id = Column(Integer, primary_key=True)

    keyword = Column(String, nullable=False)

    text = Column(Text, nullable=False)

    author = Column(String, nullable=False)

    insert_datetime_field('created', locals(), False)
