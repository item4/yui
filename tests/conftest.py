import copy
import os
import pathlib
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock

import aioresponses
import pytest
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
def anyio_backend():
    return "asyncio"


@pytest.fixture
def fx_tmpdir(tmpdir):
    return pathlib.Path(tmpdir)


@pytest.fixture(scope="session")
def database_url(request):
    return request.config.getoption("--database-url")


@pytest.fixture
async def fx_engine(database_url):
    engine = create_database_engine(database_url, echo=False)
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


@pytest.fixture
async def fx_sess(fx_engine):
    session = sessionmaker(bind=fx_engine)
    async with session() as sess:
        yield sess


def gen_config(database_url):
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
def bot_config(database_url, owner_id):
    config = gen_config(database_url)
    config.USERS["owner"] = owner_id
    return config


@pytest.fixture
def bot(request, bot_config, monkeypatch):
    if request.config.pluginmanager.hasplugin(
        "vscode_pytest",
    ) and request.config.pluginmanager.hasplugin("pytest_cov"):
        monkeypatch.setattr("resource.setrlimit", Mock())
        monkeypatch.setattr("yui.bot.ProcessPoolExecutor", ThreadPoolExecutor)
    return FakeBot(bot_config)


@pytest.fixture
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
