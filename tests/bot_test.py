import asyncio

import pytest

import ujson

from yui.api import SlackAPI
from yui.bot import APICallError, Bot
from yui.box import Box

from .util import FakeImportLib


def test_bot_init(monkeypatch, fx_config):
    importlib = FakeImportLib()

    monkeypatch.setattr("importlib.import_module", importlib.import_module)

    fx_config.MODELS = ['yui.model1', 'yui.model2']
    fx_config.HANDLERS = ['yui.handler1', 'yui.handler2']
    box = Box()
    bot = Bot(fx_config, using_box=box)

    assert bot.config == fx_config
    assert bot.channels == []
    assert bot.ims == []
    assert bot.groups == []
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
async def test_call(fx_config, response_mock):
    token = 'asdf1234'

    response_mock.post(
        'https://slack.com/api/test11',
        body=ujson.dumps({
            'res': 'hello world!',
        }),
        headers={'content-type': 'application/json'},
        status=200,
    )
    response_mock.post(
        'https://slack.com/api/test12',
        body=ujson.dumps({
            'res': 'hello world!',
            'data': {
                'extra': 'wow',
            },
        }),
        headers={'content-type': 'application/json'},
        status=200,
    )

    response_mock.post(
        'https://slack.com/api/test21',
        body=ujson.dumps({
            'error': 'aaa',
        }),
        headers={'content-type': 'application/json'},
        status=404,
    )
    response_mock.post(
        'https://slack.com/api/test22',
        body=ujson.dumps({
            'error': 'aaa',
        }),
        headers={'content-type': 'application/json'},
        status=404,
    )
    response_mock.post(
        'https://slack.com/api/test3',
        body=ujson.dumps({
            'res': 'hello world!',
        }),
        headers={'content-type': 'application/json'},
        status=200,
    )

    box = Box()
    bot = Bot(fx_config, using_box=box)

    res = await bot.call('test11')
    assert res['res'] == 'hello world!'

    res = await bot.call('test12', data={'extra': 'wow'})
    assert res['res'] == 'hello world!'
    assert res['data']['extra'] == 'wow'

    with pytest.raises(APICallError) as e:
        await bot.call('test21')
    assert str(e.value) == 'fail to call test21 with None'
    assert e.value.status_code == 404
    assert e.value.result == {'error': 'aaa'}
    assert e.value.headers['Content-Type'] == 'application/json'

    with pytest.raises(APICallError) as e:
        await bot.call('test22', data={'extra': 'wow'})
    assert str(e.value) == "fail to call test22 with {'extra': 'wow'}"
    assert e.value.status_code == 404
    assert e.value.result == {'error': 'aaa'}
    assert e.value.headers['Content-Type'] == 'application/json'

    res = await bot.call('test3', token=token)
    assert res['res'] == 'hello world!'
