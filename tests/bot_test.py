import asyncio
from collections import defaultdict
from datetime import timedelta

import pytest

from yui.api import SlackAPI
from yui.bot import Bot
from yui.box import Box
from yui.types.slack.response import APIResponse
from yui.utils import json

from .util import FakeImportLib


def test_bot_init(event_loop, monkeypatch, bot_config):
    importlib = FakeImportLib()

    monkeypatch.setattr('importlib.import_module', importlib.import_module)

    bot_config.APPS = ['yui.app1', 'yui.app2']
    box = Box()
    bot = Bot(bot_config, event_loop, using_box=box)

    assert bot.config == bot_config
    assert bot.channels == []
    assert bot.ims == []
    assert bot.groups == []
    assert bot.restart is False
    assert isinstance(bot.api, SlackAPI)
    assert bot.box is box
    assert isinstance(bot.queue, asyncio.Queue)
    assert importlib.import_queue == [
        'yui.app1',
        'yui.app2',
    ]


@pytest.mark.asyncio
async def test_call(event_loop, bot_config, response_mock):
    token = 'asdf1234'

    response_mock.post(
        'https://slack.com/api/test11',
        body=json.dumps({'res': 'hello world!'}),
        headers={'content-type': 'application/json'},
        status=200,
    )
    response_mock.post(
        'https://slack.com/api/test12',
        body=json.dumps({'res': 'hello world!', 'data': {'extra': 'wow'}}),
        headers={'content-type': 'application/json'},
        status=200,
    )

    response_mock.post(
        'https://slack.com/api/test21',
        body=json.dumps({'error': 'aaa'}),
        headers={'content-type': 'application/json'},
        status=404,
    )
    response_mock.post(
        'https://slack.com/api/test22',
        body=json.dumps({'error': 'aaa'}),
        headers={'content-type': 'application/json'},
        status=404,
    )
    response_mock.post(
        'https://slack.com/api/test3',
        body=json.dumps({'res': 'hello world!'}),
        headers={'content-type': 'application/json'},
        status=200,
    )

    box = Box()
    bot = Bot(bot_config, event_loop, using_box=box)
    bot.api.throttle_interval = defaultdict(lambda: timedelta(0))

    res = await bot.call('test11')
    assert res == APIResponse(
        body={'res': 'hello world!'},
        status=200,
        headers={'content-type': 'application/json'},
    )

    res = await bot.call('test12', data={'extra': 'wow'})
    assert res == APIResponse(
        body={'res': 'hello world!', 'data': {'extra': 'wow'}},
        status=200,
        headers={'content-type': 'application/json'},
    )

    res = await bot.call('test21')
    assert res == APIResponse(
        body={'error': 'aaa'},
        status=404,
        headers={'content-type': 'application/json'},
    )

    res = await bot.call('test22', data={'extra': 'wow'})
    assert res == APIResponse(
        body={'error': 'aaa'},
        status=404,
        headers={'content-type': 'application/json'},
    )

    res = await bot.call('test3', token=token)
    assert res == APIResponse(
        body={'res': 'hello world!'},
        status=200,
        headers={'content-type': 'application/json'},
    )
