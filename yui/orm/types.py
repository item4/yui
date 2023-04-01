from typing import Annotated
from typing import TypeAlias

from sqlalchemy.orm import mapped_column

PrimaryKey: TypeAlias = Annotated[int, mapped_column(primary_key=True)]
Text: TypeAlias = Annotated[str, mapped_column(deferred=True)]
