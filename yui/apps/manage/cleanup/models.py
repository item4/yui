from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String

from ....orm import Base


class EventLog(Base):
    """EventLog for cleanup function"""

    __tablename__ = 'event_log'

    id = Column(Integer, primary_key=True)

    ts = Column(String, nullable=False)

    channel = Column(String, nullable=False)
