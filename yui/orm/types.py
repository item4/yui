from typing import Annotated

from sqlalchemy.orm import mapped_column

type PrimaryKey = Annotated[int, mapped_column(primary_key=True)]
type Text = Annotated[str, mapped_column(deferred=True)]
