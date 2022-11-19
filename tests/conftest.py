import copy
import os
import pathlib

import aioresponses
import emcache
import pytest
import pytest_asyncio
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.sql.expression import text

from yui.cache import Cache
from yui.config import Config
from yui.config import DEFAULT
from yui.orm import Base
from yui.orm import create_database_engine
from yui.orm import sessionmaker

from .util import FakeBot

DEFAULT_DATABASE_URL = "sqlite://"


def pytest_addoption(parser):
    parser.addoption(
        "--database-url",
        type=str,
        default=os.getenv("YUI_TEST_DATABASE_URL", DEFAULT_DATABASE_URL),
        help="Database URL for testing." "[default: %(default)s]",
    )


@pytest.fixture()
def fx_tmpdir(tmpdir):
    return pathlib.Path(tmpdir)


@pytest_asyncio.fixture()
async def fx_engine(request):
    try:
        database_url = request.config.getoption("--database-url")
    except ValueError:
        database_url = None
    config = gen_config(request)
    if database_url:
        config.DATABASE_URL = database_url
    engine = create_database_engine(database_url, False)
    try:
        metadata = Base.metadata
        async with engine.begin() as conn:
            await conn.run_sync(metadata.drop_all)
            await conn.run_sync(metadata.create_all)
        yield engine
        async with engine.begin() as conn:
            await conn.run_sync(metadata.drop_all)
    finally:
        await engine.dispose()


@pytest_asyncio.fixture()
async def fx_sess(fx_engine):
    metadata = Base.metadata
    error = False
    async with fx_engine.begin() as conn:
        try:
            await conn.execute(text("SET CONSTRAINTS ALL IMMEDIATE;"))
        except ProgrammingError:
            error = True

        for table in reversed(metadata.sorted_tables):
            try:
                await conn.execute(
                    text(
                        "TRUNCATE TABLE {} RESTART IDENTITY CASCADE;".format(
                            table.name,
                        )
                    )
                )
            except ProgrammingError:
                error = True

        try:
            await conn.execute(text("SET CONSTRAINTS ALL IMMEDIATE;"))
        except ProgrammingError:
            error = True

    if error:
        metadata = Base.metadata
        async with fx_engine.begin() as conn:
            await conn.run_sync(metadata.drop_all)
            await conn.run_sync(metadata.create_all)

    session = sessionmaker(bind=fx_engine)
    async with session() as sess:
        yield sess


def gen_config(request):
    try:
        database_url = request.config.getoption("--database-url")
    except ValueError:
        database_url = "sqlite:///"
    cfg = copy.deepcopy(DEFAULT)
    cfg.update(
        dict(
            DEBUG=True,
            DATABASE_URL=database_url,
            APP_TOKEN="TEST_APP_TOKEN",
            BOT_TOKEN="TEST_BOT_TOKEN",
            REGISTER_CRONTAB=False,
            CHANNELS={},
            USERS={},
            WEBSOCKETDEBUGGERURL="",
        )
    )
    config = Config(**cfg)
    config.LOGGING["loggers"]["yui"]["handlers"] = ["console"]
    del config.LOGGING["handlers"]["file"]
    return config


@pytest.fixture()
def bot():
    return FakeBot()


@pytest.fixture()
def bot_config(request):
    return gen_config(request)


@pytest.fixture(scope="module")
async def cache():
    mc = await emcache.create_client(
        [emcache.MemcachedHostAddress("localhost", 11211)]
    )  # FIXME
    yield Cache(mc, "YUI_TEST_")
    await mc.close()


@pytest.fixture()
def response_mock():
    with aioresponses.aioresponses() as m:
        yield m
