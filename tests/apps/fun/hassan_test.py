import pytest

from yui.apps.fun.hassan import hassan


@pytest.mark.anyio
async def test_hassan_handler(bot):
    event = bot.create_message(text="똑바로 서라 유이")

    assert not await hassan(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"] == f"저한테 왜 그러세요 <@{event.user}>님?"

    event = bot.create_message(text="아무말 대잔치")

    assert await hassan(bot, event)

    assert not bot.call_queue
