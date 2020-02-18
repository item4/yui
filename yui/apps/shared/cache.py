from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String

from ...orm import Base
from ...orm.columns import DateTimeAtColumn, DateTimeColumn, TimezoneColumn
from ...orm.types import JSONType


class JSONCache(Base):

    __tablename__ = 'json_cache'

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False, unique=True)

    body = Column(JSONType)

    created_datetime = DateTimeColumn(nullable=False)

    created_timezone = TimezoneColumn()

    created_at = DateTimeAtColumn('created')
