from typing import Optional
from typing import Type

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import Pool

from ..config import Config


def create_database_engine(
    url: str,
    echo: bool,
    poolclass: Optional[Type[Pool]] = None,
) -> AsyncEngine:
    return create_async_engine(
        url,
        echo=echo,
        poolclass=poolclass,
        pool_pre_ping=True,
    )


def get_database_engine(
    config: Config,
    poolclass: Optional[Type[Pool]] = None,
) -> AsyncEngine:
    try:
        engine = config.DATABASE_ENGINE
    except AttributeError:
        url = config.DATABASE_URL
        echo = config.DATABASE_ECHO
        engine = create_database_engine(url, echo, poolclass)
    else:
        if engine is None:
            url = config.DATABASE_URL
            echo = config.DATABASE_ECHO
            engine = create_database_engine(url, echo, poolclass)

    return engine
