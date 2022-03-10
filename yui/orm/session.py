import contextlib
from collections.abc import Iterator
from typing import NamedTuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.pool import NullPool

from .engine import create_database_engine


class EngineConfig(NamedTuple):

    url: str
    echo: bool


def make_session(*args, **kwargs) -> AsyncSession:
    kwargs['expire_on_commit'] = False
    return AsyncSession(*args, **kwargs)


@contextlib.contextmanager
def subprocess_session_manager(
    engine_config: EngineConfig,
    *args,
    **kwargs,
) -> Iterator[AsyncSession]:
    engine = create_database_engine(
        engine_config.url,
        engine_config.echo,
        NullPool,
    )
    session = make_session(bind=engine, *args, **kwargs)
    yield session
    engine.dispose()
