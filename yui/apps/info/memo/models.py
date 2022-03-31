from sqlalchemy.schema import Column
from sqlalchemy.types import Integer
from sqlalchemy.types import String
from sqlalchemy.types import Text

from ....orm import Base
from ....orm.columns import DateTimeAtColumn
from ....orm.columns import DateTimeColumn
from ....orm.columns import TimezoneColumn


class Memo(Base):
    """Memo"""

    __tablename__ = "memo"

    id = Column(Integer, primary_key=True)

    keyword = Column(String, nullable=False)

    text = Column(Text, nullable=False)

    author = Column(String, nullable=False)

    created_datetime = DateTimeColumn(nullable=False)

    created_timezone = TimezoneColumn()

    created_at = DateTimeAtColumn("created")
