from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker as _sessionmaker


def sessionmaker(*args, **kwargs):
    kwargs["class_"] = AsyncSession
    kwargs["expire_on_commit"] = False
    return _sessionmaker(*args, **kwargs)
