from datetime import datetime

from sqlalchemy import types
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import MappedAsDataclass
from sqlalchemy.orm import registry

from .columns import DateTime
from .types import PrimaryKey
from .types import Text


class Base(MappedAsDataclass, DeclarativeBase):
    registry = registry(
        type_annotation_map={
            PrimaryKey: types.Integer,
            Text: types.Text,
            datetime: DateTime(timezone=True),
        }
    )
