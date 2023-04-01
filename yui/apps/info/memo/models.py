from datetime import datetime

from sqlalchemy.orm import Mapped

from ....orm import Base
from ....orm.types import PrimaryKey
from ....orm.types import Text


class Memo(Base):
    """Memo"""

    __tablename__ = "memo"

    id: Mapped[PrimaryKey]

    keyword: Mapped[str]

    text: Mapped[Text]

    author: Mapped[str]

    created_at: Mapped[datetime]
