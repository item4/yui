from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, Text

from ..orm import Base


class SiteSub(Base):
    """Site diff subscribe"""

    __tablename__ = 'site_sub'

    id = Column(Integer, primary_key=True)

    url = Column(String, nullable=False)

    user = Column(String(10), nullable=False)

    body = Column(Text)
