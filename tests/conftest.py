import copy
import pathlib

from attrdict import AttrDict

import pytest

from sqlalchemy.exc import ProgrammingError

from yui.bot import Bot, Session
from yui.config import DEFAULT
from yui.orm import Base


@pytest.fixture()
def fx_tmpdir(tmpdir):
    return pathlib.Path(tmpdir)


@pytest.yield_fixture(scope='session')
def fx_engine():
    config = AttrDict(copy.deepcopy(DEFAULT))
    config.DEBUG = True
    config.DATABASE_URL = 'sqlite:///'
    config.MODELS = ['yui.models']
    config.HANDLERS = ['yui.handlers']
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
