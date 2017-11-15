import asyncio
import copy

from attrdict import AttrDict

from mocket.mocket import Mocketizer
from mocket.mockhttp import Entry

import pytest

import ujson

from yui.api import SlackAPI
from yui.bot import APICallError, Bot
from yui.box import box
from yui.config import DEFAULT

from .util import FakeImportLib


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
async def test_call():
    with Mocketizer(None):
        token = 'asdf1234'

        Entry.single_register(
            Entry.POST,
            'https://slack.com/api/test11',
            body=ujson.dumps({
                'res': 'hello world!',
                'data': {
                    'token': token,
                },
            }),
            headers={'content-type': 'application/json'},
            status=200,
        )
        Entry.single_register(
            Entry.POST,
            'https://slack.com/api/test12',
            body=ujson.dumps({
                'res': 'hello world!',
                'data': {
                    'token': token,
                    'extra': 'wow',
                },
            }),
            headers={'content-type': 'application/json'},
            status=200,
        )

        Entry.single_register(
            Entry.POST,
            'https://slack.com/api/test21',
            body='',
            headers={'content-type': 'application/json'},
            status=404,
        )
        Entry.single_register(
            Entry.POST,
            'https://slack.com/api/test22',
            body='',
            headers={'content-type': 'application/json'},
            status=404,
        )

        config = AttrDict(copy.deepcopy(DEFAULT))
        config.DATABASE_URL = 'sqlite:///'
        config.TOKEN = 'asdf1234'
        config['LOGGING']['loggers']['yui']['handlers'] = ['console']
        del config['LOGGING']['handlers']['file']
        bot = Bot(config)

        res = await bot.call('test11')
        assert res['res'] == 'hello world!'
        assert res['data']['token'] == 'asdf1234'

        res = await bot.call('test12', data={'extra': 'wow'})
        assert res['res'] == 'hello world!'
        assert res['data']['extra'] == 'wow'
        assert res['data']['token'] == 'asdf1234'

        with pytest.raises(APICallError) as e:
            await bot.call('test21')
        assert str(e.value) == 'fail to call test21 with None'

        with pytest.raises(APICallError) as e:
            await bot.call('test22', data={'extra': 'wow'})
        assert str(e.value) == "fail to call test22 with {'extra': 'wow'}"
