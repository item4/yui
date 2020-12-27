import copy
import os
import pathlib

import aiomcache

import aioresponses

import pytest

from sqlalchemy.exc import ProgrammingError

from yui.bot import Bot
from yui.box import Box
from yui.cache import Cache
from yui.config import Config
from yui.config import DEFAULT
from yui.orm import Base
from yui.orm import make_session

from .util import FakeBot


DEFAULT_DATABASE_URL = 'sqlite://'


def pytest_addoption(parser):
    parser.addoption(
        '--database-url',
        type=str,
        default=os.getenv('YUI_TEST_DATABASE_URL', DEFAULT_DATABASE_URL),
        help='Database URL for testing.' '[default: %default]',
    )


@pytest.fixture()
def fx_tmpdir(tmpdir):
    return pathlib.Path(tmpdir)


@pytest.yield_fixture(scope='session')
def fx_engine(request):
    try:
        database_url = request.config.getoption('--database-url')
    except ValueError:
        database_url = None
    config = gen_config(request)
    if database_url:
        config.DATABASE_URL = database_url
    bot = Bot(config, using_box=Box())
    engine = bot.config.DATABASE_ENGINE
    try:
        metadata = Base.metadata
        metadata.drop_all(bind=engine)
        metadata.create_all(bind=engine)
        yield engine
        metadata.drop_all(bind=engine)
    finally:
        engine.dispose()


@pytest.yield_fixture()
def fx_sess(fx_engine):
    metadata = Base.metadata
    foreign_key_turn_off = {
        'mysql': 'SET FOREIGN_KEY_CHECKS=0;',
        'postgresql': 'SET CONSTRAINTS ALL DEFERRED;',
        'sqlite': 'PRAGMA foreign_keys = OFF;',
    }
    foreign_key_turn_on = {
        'mysql': 'SET FOREIGN_KEY_CHECKS=1;',
        'postgresql': 'SET CONSTRAINTS ALL IMMEDIATE;',
        'sqlite': 'PRAGMA foreign_keys = ON;',
    }
    truncate_query = {
        'mysql': 'TRUNCATE TABLE {};',
        'postgresql': 'TRUNCATE TABLE {} RESTART IDENTITY CASCADE;',
        'sqlite': 'DELETE FROM {};',
    }
    error = False
    with fx_engine.begin() as conn:
        try:
            conn.execute(foreign_key_turn_off[fx_engine.name])
        except ProgrammingError:
            error = True

        for table in reversed(metadata.sorted_tables):
            try:
                conn.execute(truncate_query[fx_engine.name].format(table.name))
            except ProgrammingError:
                error = True

        try:
            conn.execute(foreign_key_turn_on[fx_engine.name])
        except ProgrammingError:
            error = True

    if error:
        metadata = Base.metadata
        metadata.drop_all(bind=fx_engine)
        metadata.create_all(bind=fx_engine)

    sess = make_session(bind=fx_engine)
    yield sess
    sess.rollback()


def gen_config(request):
    try:
        database_url = request.config.getoption('--database-url')
    except ValueError:
        database_url = 'sqlite:///'
    cfg = copy.deepcopy(DEFAULT)
    cfg.update(
        dict(
            DEBUG=True,
            DATABASE_URL=database_url,
            TOKEN='asdf1234',
            REGISTER_CRONTAB=False,
            CHANNELS={},
            USERS={},
            WEBSOCKETDEBUGGERURL='',
        )
    )
    config = Config(**cfg)
    config.LOGGING['loggers']['yui']['handlers'] = ['console']
    del config.LOGGING['handlers']['file']
    return config


@pytest.fixture()
def bot():
    return FakeBot()


@pytest.fixture()
def bot_config(request):
    return gen_config(request)


@pytest.fixture(scope='module')
async def cache():
    mc = aiomcache.Client(host='localhost', port=11211)  # FIXME
    return Cache(mc, 'YUI_TEST_')


@pytest.yield_fixture()
def response_mock():
    with aioresponses.aioresponses() as m:
        yield m
