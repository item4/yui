import asyncio
from collections import defaultdict
from datetime import timedelta

import pytest

from yui.api import SlackAPI
from yui.bot import Bot
from yui.box import Box
from yui.types.slack.response import APIResponse

from .util import FakeImportLib


def test_bot_init(monkeypatch, bot_config):
    importlib = FakeImportLib()

    monkeypatch.setattr("importlib.import_module", importlib.import_module)

    bot_config.APPS = ["yui.app1", "yui.app2"]
    box = Box()
    bot = Bot(bot_config, using_box=box)

    assert bot.config == bot_config
    assert bot.restart is False
    assert isinstance(bot.api, SlackAPI)
    assert bot.box is box
    assert isinstance(bot.queue, asyncio.Queue)
    assert importlib.import_queue == [
        "yui.app1",
        "yui.app2",
    ]


@pytest.mark.asyncio
async def test_call(bot_config, response_mock):
    token = "asdf1234"  # noqa: S105

    response_mock.post(
        "https://slack.com/api/test11",
        payload={"res": "hello world!"},
    )
    response_mock.post(
        "https://slack.com/api/test12",
        payload={"res": "hello world!", "data": {"extra": "wow"}},
    )

    response_mock.post(
        "https://slack.com/api/test21",
        payload={"error": "aaa"},
        status=404,
    )
    response_mock.post(
        "https://slack.com/api/test22",
        payload={"error": "aaa"},
        status=404,
    )
    response_mock.post(
        "https://slack.com/api/test3",
        payload={"res": "hello world!"},
    )

    box = Box()
    bot = Bot(bot_config, using_box=box)
    bot.api.throttle_interval = defaultdict(lambda: timedelta(0))

    resp = await bot.call("test11")
    assert isinstance(resp, APIResponse)
    assert resp.body == {"res": "hello world!"}
    assert resp.status == 200
    assert resp.headers["Content-Type"] == "application/json"

    resp = await bot.call("test12", data={"extra": "wow"})
    assert isinstance(resp, APIResponse)
    assert resp.body == {"res": "hello world!", "data": {"extra": "wow"}}
    assert resp.status == 200
    assert resp.headers["Content-Type"] == "application/json"

    resp = await bot.call("test21")
    assert isinstance(resp, APIResponse)
    assert resp.body == {"error": "aaa"}
    assert resp.status == 404
    assert resp.headers["Content-Type"] == "application/json"

    resp = await bot.call("test22", data={"extra": "wow"})
    assert isinstance(resp, APIResponse)
    assert resp.body == {"error": "aaa"}
    assert resp.status == 404
    assert resp.headers["Content-Type"] == "application/json"

    resp = await bot.call("test3", token=token)
    assert isinstance(resp, APIResponse)
    assert resp.body == {"res": "hello world!"}
    assert resp.status == 200
    assert resp.headers["Content-Type"] == "application/json"


@pytest.mark.asyncio
async def test_call_json(bot_config, response_mock, channel_id):
    response_mock.post(
        "https://slack.com/api/chat.postMessage",
        payload={"ok": True},
    )

    box = Box()
    bot = Bot(bot_config, using_box=box)
    bot.api.throttle_interval = defaultdict(lambda: timedelta(0))

    resp = await bot.api.chat.postMessage(channel_id, "hello world!")
    assert isinstance(resp, APIResponse)
    assert resp.is_ok()
    assert resp.body == {"ok": True}
    assert resp.status == 200
    assert resp.headers["Content-Type"] == "application/json"
