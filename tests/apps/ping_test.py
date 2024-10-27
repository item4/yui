import pytest

from yui.apps.ping import ping


@pytest.mark.asyncio
async def test_ping_command(bot):
    event = bot.create_message("C1", "U1")

    await ping(bot, event)
    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"] == "<@U1>, pong!"
