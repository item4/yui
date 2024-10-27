import pytest

from yui.apps.info.about import MESSAGE
from yui.apps.info.about import about


@pytest.mark.asyncio
async def test_about_command(bot):
    event = bot.create_message("C1", "U1", "1234.56")

    await about(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"] == MESSAGE.format(prefix=bot.config.PREFIX)
    assert said.data["thread_ts"] == "1234.56"
