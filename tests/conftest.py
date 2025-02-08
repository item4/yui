import copy
import os
import pathlib

import aioresponses
import pytest
import pytest_asyncio
from valkey.asyncio import Valkey

from yui.cache import Cache
from yui.config import Config
from yui.config import DEFAULT
from yui.orm import Base
from yui.orm import create_database_engine
from yui.orm import sessionmaker
from yui.utils.datetime import datetime

from .util import FakeBot

DEFAULT_DATABASE_URL = "sqlite://"


def pytest_addoption(parser):
    parser.addoption(
        "--database-url",
        type=str,
        default=os.getenv("YUI_TEST_DATABASE_URL", DEFAULT_DATABASE_URL),
        help="Database URL for testing.[default: %(default)s]",
    )


@pytest.fixture
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
        {
            "DEBUG": True,
            "DATABASE_URL": database_url,
            "APP_TOKEN": "TEST_APP_TOKEN",
            "BOT_TOKEN": "TEST_BOT_TOKEN",
            "REGISTER_CRONTAB": False,
            "CHANNELS": {},
            "USERS": {},
            "WEBSOCKETDEBUGGERURL": "",
        },
    )
    config = Config(**cfg)
    config.LOGGING["loggers"]["yui"]["handlers"] = ["console"]
    del config.LOGGING["handlers"]["file"]
    return config


@pytest.fixture(scope="session")
def owner_id():
    return "U0000"


@pytest.fixture
def bot_config(request, owner_id):
    config = gen_config(request)
    config.USERS["owner"] = owner_id
    return config


@pytest.fixture
def bot(bot_config):
    return FakeBot(bot_config)


@pytest_asyncio.fixture()
async def cache():
    valkey_client = Valkey.from_url("valkey://localhost")
    c = Cache(valkey_client, "YUI_TEST_")
    yield c
    await c.close()


@pytest.fixture
def response_mock():
    with aioresponses.aioresponses() as m:
        yield m


@pytest.fixture(scope="session")
def sunday():
    return datetime(2022, 11, 6)


@pytest.fixture(scope="session")
def channel_id():
    return "C0FFEE"


@pytest.fixture(scope="session")
def user_id():
    return "U12345"
