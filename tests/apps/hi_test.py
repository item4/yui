import pytest

from yui.apps.hi import hi


@pytest.mark.anyio
async def test_hi_handler(bot):
    event = bot.create_message(text="안녕 유이")

    await hi(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"] == f"안녕하세요! <@{event.user}>"

    event = bot.create_message(text="유이 안녕")

    await hi(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"] == f"안녕하세요! <@{event.user}>"

    event = bot.create_message(text="아무말 대잔치")

    await hi(bot, event)

    assert not bot.call_queue
