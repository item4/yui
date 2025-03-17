import pytest

from yui.apps.ping import ping


@pytest.mark.anyio
async def test_ping_command(bot):
    event = bot.create_message()

    await ping(bot, event)
    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"] == f"<@{event.user}>, pong!"
