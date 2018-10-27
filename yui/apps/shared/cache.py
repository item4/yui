from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String

from ...orm import Base
from ...orm.type import JSONType
from ...orm.utils import insert_datetime_field


class JSONCache(Base):

    __tablename__ = 'json_cache'

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False, unique=True)

    body = Column(JSONType)

    insert_datetime_field('created', locals(), False)
