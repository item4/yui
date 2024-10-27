import pytest

from yui.apps.owner.say import say
from yui.types.slack.response import APIResponse


@pytest.mark.asyncio
async def test_say_command(bot, owner_id, user_id):
    test = bot.create_channel("C2", "test")

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

    event = bot.create_message(user_id=owner_id)

    await say(bot, event, None, None, text)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"] == text

    await say(bot, event, test.id, None, text)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == test.id
    assert said.data["text"] == text

    await say(bot, event, None, user_id, text)

    conversations_open = bot.call_queue.pop(0)
    assert conversations_open.method == "conversations.open"
    assert conversations_open.data["users"] == user_id
    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == user_id.replace("U", "D")
    assert said.data["text"] == text

    await say(bot, event, test.id, user_id, text)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert (
        said.data["text"]
        == "`--channel` 옵션과 `--user` 옵션은 동시에 사용할 수 없어요!"
    )

    event = bot.create_message()

    await say(bot, event, None, None, "죽어라!")

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert (
        said.data["text"]
        == f"<@{event.user}> 이 명령어는 아빠만 사용할 수 있어요!"
    )
