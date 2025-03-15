from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import Pool


def create_database_engine(
    url: str,
    *,
    echo: bool,
    poolclass: type[Pool] | None = None,
) -> AsyncEngine:
    return create_async_engine(
        url,
        future=True,
        echo=echo,
        poolclass=poolclass,
        pool_pre_ping=True,
    )
