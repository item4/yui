from datetime import datetime

from sqlalchemy import types
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import registry

from .columns import DateTime
from .types import PrimaryKey
from .types import Text


class Base(DeclarativeBase):
    registry = registry(
        type_annotation_map={
            PrimaryKey: types.Integer,
            Text: types.Text,
            datetime: DateTime(timezone=True),
        },
    )
