import pytest

from yui.apps.welcome.item4 import welcome_item4
from yui.apps.welcome.the_9xd import welcome_9xd
from yui.event import create_event
from yui.types.slack.response import APIResponse

from ..util import FakeBot


@pytest.mark.asyncio
async def test_welcome_item4_handler(bot_config):
    bot_config.PREFIX = "."
    bot_config.CHANNELS = {
        "welcome": "C1",
    }
    bot = FakeBot(bot_config)
    event = create_event("team_join", {"user": "U1"})

    await welcome_item4(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"].startswith(
        "<@U1>님 item4 개인 Slack에 오신걸 환영합니다! :tada:",
    )
    assert "`.도움`" in said.data["text"]


@pytest.mark.asyncio
async def test_welcome_9xd_handler(bot_config):
    bot_config.PREFIX = "."
    bot_config.CHANNELS = {
        "welcome": "C1",
    }
    bot = FakeBot(bot_config)
    event = create_event("team_join", {"user": "U1"})

    @bot.response("chat.postMessage")
    def team_join(data):
        return APIResponse(
            body={"ok": True, "ts": "1234.5678"},
            status=200,
            headers={},
        )

    await welcome_9xd(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"].startswith(
        "<@U1>님 9XD Slack에 오신걸 환영합니다! :tada:",
    )
    assert "`.도움`" in said.data["text"]

    thread = bot.call_queue.pop(0)
    assert thread.method == "chat.postMessage"
    assert thread.data["channel"] == "C1"
    assert thread.data["text"].startswith(
        "9XD Slack에는 다음과 같은 채널들이 있으니 참가해보셔도 좋을 것 같아요!",
    )
    assert thread.data["thread_ts"] == "1234.5678"
