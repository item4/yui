import asyncio
import copy

from attrdict import AttrDict

import pytest

import ujson

from yui.api import SlackAPI
from yui.bot import APICallError, Bot
from yui.box import box
from yui.config import DEFAULT

from .util import FakeClientSession, FakeImportLib


def test_bot_init(monkeypatch):
    importlib = FakeImportLib()

    monkeypatch.setattr("importlib.import_module", importlib.import_module)

    config = AttrDict(copy.deepcopy(DEFAULT))
    config.DEBUG = True
    config.DATABASE_URL = 'sqlite:///'
    config.MODELS = ['yui.model1', 'yui.model2']
    config.HANDLERS = ['yui.handler1', 'yui.handler2']
    config['LOGGING']['loggers']['yui']['handlers'] = ['console']
    del config['LOGGING']['handlers']['file']
    bot = Bot(config)

    assert bot.config == config
    assert bot.channels == {}
    assert bot.loop is None
    assert bot.restart is False
    assert isinstance(bot.api, SlackAPI)
    assert bot.box is box
    assert isinstance(bot.queue, asyncio.Queue)
    assert importlib.import_queue == [
        'yui.handler1',
        'yui.handler2',
        'yui.model1',
        'yui.model2',
    ]


@pytest.mark.asyncio
async def test_call(monkeypatch):
    client_session = FakeClientSession()

    @client_session.post('https://slack.com/api/test1')
    def test1(**kwargs):
        kwargs['data'] = {x[0]['name']: x[2] for x in kwargs['data']._fields}
        kwargs.update({
            'res': 'hello world!',
        })
        return ujson.dumps(kwargs)

    @client_session.post('https://slack.com/api/test2')
    def test2(**kwargs):
        return 404, ujson.dumps(kwargs)

    monkeypatch.setattr('aiohttp.ClientSession', client_session)

    config = AttrDict(copy.deepcopy(DEFAULT))
    config.DATABASE_URL = 'sqlite:///'
    config.TOKEN = 'asdf1234'
    config['LOGGING']['loggers']['yui']['handlers'] = ['console']
    del config['LOGGING']['handlers']['file']
    bot = Bot(config)

    res = await bot.call('test1')
    assert res['res'] == 'hello world!'
    assert res['data']['token'] == 'asdf1234'

    res = await bot.call('test1', data={'extra': 'wow'})
    assert res['res'] == 'hello world!'
    assert res['data']['extra'] == 'wow'
    assert res['data']['token'] == 'asdf1234'

    with pytest.raises(APICallError) as e:
        await bot.call('test2')
    assert str(e.value) == 'fail to call test2 with None'

    with pytest.raises(APICallError) as e:
        await bot.call('test2', data={'extra': 'wow'})
    assert str(e.value) == "fail to call test2 with {'extra': 'wow'}"
