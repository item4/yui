import pytest

from yui.apps.owner.say import say
from yui.types.slack.response import APIResponse

from ...util import FakeBot


@pytest.mark.asyncio
async def test_say_command(bot_config):
    bot_config.USERS["owner"] = "U1"
    bot = FakeBot(bot_config)
    test = bot.create_channel("C2", "test")
    poh = bot.create_user("U2", "PoH")

    @bot.response("conversations.open")
    def callback(data):
        return APIResponse(
            body={
                "ok": True,
                "channel": {
                    "id": data["users"].split(",")[0].replace("U", "D"),
                },
            },
            status=200,
            headers={},
        )

    text = "안녕하세요! 하고 유이인 척 하기"

    event = bot.create_message("C1", "U1")

    await say(bot, event, None, None, text)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == text

    await say(bot, event, test.id, None, text)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C2"
    assert said.data["text"] == text

    await say(bot, event, None, poh.id, text)

    conversations_open = bot.call_queue.pop(0)
    assert conversations_open.method == "conversations.open"
    assert conversations_open.data["users"] == "U2"
    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "D2"
    assert said.data["text"] == text

    await say(bot, event, test.id, poh.id, text)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert (
        said.data["text"]
        == "`--channel` 옵션과 `--user` 옵션은 동시에 사용할 수 없어요!"
    )

    event = bot.create_message("C1", "U2")

    await say(bot, event, None, None, "죽어라!")

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == "<@U2> 이 명령어는 아빠만 사용할 수 있어요!"
