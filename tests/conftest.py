import copy
import os
import pathlib

import aioresponses

from attrdict import AttrDict

import pytest

from sqlalchemy.exc import ProgrammingError

from yui.bot import Bot, Session
from yui.config import DEFAULT
from yui.orm import Base


DEFAULT_DATABASE_URL = 'sqlite://'


def pytest_addoption(parser):
    parser.addoption('--database-url', type='string',
                     default=os.getenv('YUI_TEST_DATABASE_URL',
                                       DEFAULT_DATABASE_URL),
                     help='Database URL for testing.'
                          '[default: %default]')


@pytest.fixture()
def fx_tmpdir(tmpdir):
    return pathlib.Path(tmpdir)


@pytest.yield_fixture(scope='session')
def fx_engine(request):
    try:
        database_url = request.config.getoption('--database-url')
    except ValueError:
        database_url = None

    config = AttrDict(copy.deepcopy(DEFAULT))
    config.DEBUG = True
    config.DATABASE_URL = database_url
    config.MODELS = []
    config.HANDLERS = []
    config['LOGGING']['loggers']['yui']['handlers'] = ['console']
    config.REGISTER_CRONTAB = False
    del config['LOGGING']['handlers']['file']
    bot = Bot(config)
    engine = bot.config.DATABASE_ENGINE
    try:
        metadata = Base.metadata
        metadata.drop_all(bind=engine)
        metadata.create_all(bind=engine)
        yield engine
        metadata.drop_all(bind=engine)
    finally:
        engine.dispose()


@pytest.yield_fixture(scope='session')
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

    sess = Session(bind=fx_engine)
    yield sess
    sess.rollback()


@pytest.yield_fixture()
def response_mock():
    with aioresponses.aioresponses() as m:
        yield m
