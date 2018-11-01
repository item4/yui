import enum
from typing import Dict

from sqlalchemy.schema import Column
from sqlalchemy.types import Boolean, Integer, String

from sqlalchemy_utils.types import ChoiceType

from ....orm import Base


@enum.unique
class Server(enum.IntEnum):
    """Server."""

    japan = 1
    worldwide = 2


SERVER_LABEL: Dict[Server, str] = {
    Server.japan: '일본',
    Server.worldwide: '글로벌',
}


class Notice(Base):
    """Notice."""

    __tablename__ = 'saomd_notice'

    id = Column(Integer, primary_key=True)

    notice_id = Column(Integer, nullable=False)

    server = Column(ChoiceType(Server, impl=Integer()), nullable=False)

    title = Column(String, nullable=False)

    duration = Column(String)

    short_description = Column(String)

    is_deleted = Column(Boolean, default=False)
