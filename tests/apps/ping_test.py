import pytest

from yui.apps.ping import ping


@pytest.mark.asyncio()
async def test_ping_command(bot):
    bot.add_channel("C1", "general")
    bot.add_user("U1", "item4")
    event = bot.create_message("C1", "U1")

    await ping(bot, event)
    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == "<@U1>, pong!"
