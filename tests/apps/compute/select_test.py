import pytest

from yui.apps.compute.select import select


@pytest.mark.asyncio
async def test_select_command(bot):
    event = bot.create_message()
    seed = 1

    await select(bot, event, ["cat", "dog"], seed)
    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"] == "선택결과: cat"

    await select(bot, event, ["키리가야 카즈토", "유지오"], seed)
    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"] == "선택결과: 키리가야 카즈토"
