import contextlib
from typing import Iterator, NamedTuple

from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool

from .engine import create_database_engine

__all__ = (
    'EngineConfig',
    'make_session',
    'subprocess_session_manager',
)


class EngineConfig(NamedTuple):

    url: str
    echo: bool


def make_session(*args, **kwargs) -> Session:  # noqa
    kwargs['autocommit'] = True
    return Session(*args, **kwargs)


@contextlib.contextmanager
def subprocess_session_manager(
    engine_config: EngineConfig,
    *args,
    **kwargs,
) -> Iterator[Session]:
    engine = create_database_engine(
        engine_config.url,
        engine_config.echo,
        NullPool,
    )
    session = make_session(bind=engine, *args, **kwargs)
    yield session
    engine.dispose()
