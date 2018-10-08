import contextlib
from typing import Iterator, NamedTuple, Optional, Type

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool, Pool

from yui.config import Config

__all__ = (
    'Base',
    'EngineConfig',
    'get_database_engine',
    'make_session',
    'subprocess_session_manager',
)

Base = declarative_base()


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
    engine = _get_database_engine(
        engine_config.url,
        engine_config.echo,
        NullPool,
    )
    session = make_session(bind=engine, *args, **kwargs)
    yield session
    engine.dispose()


def get_database_engine(
    config: Config,
    poolclass: Optional[Type[Pool]]=None,
) -> Engine:
    try:
        return config.DATABASE_ENGINE
    except AttributeError:
        url = config.DATABASE_URL
        echo = config.DATABASE_ECHO
        engine = _get_database_engine(url, echo, poolclass)

        return engine


def _get_database_engine(
    url: str,
    echo: bool,
    poolclass: Optional[Type[Pool]]=None,
) -> Engine:
    return create_engine(
        url,
        echo=echo,
        poolclass=poolclass,
        pool_pre_ping=True,
    )
