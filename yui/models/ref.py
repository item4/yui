from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, Text

from ..orm import Base


class Ref(Base):
    """Reference HTML"""

    __tablename__ = 'ref'

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False, unique=True)

    body = Column(Text)
