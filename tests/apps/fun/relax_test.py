import pytest

from yui.apps.fun.relax import relax

from ...util import FakeBot


@pytest.mark.asyncio
async def test_relax_command(bot_config):
    bot_config.USERS["villain"] = "U2"
    bot = FakeBot(bot_config)
    event = bot.create_message(text="")

    await relax(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert (
        said.data["text"] == "유이에게 나쁜 것을 주입하려는 사악한 <@U2>!"
        " 악당은 방금 이 너굴맨이 처치했으니 안심하라구!"
    )
    assert said.data["username"] == "너굴맨"

    event = bot.create_message(text="스테이크")

    await relax(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert (
        said.data["text"] == "사람들에게 스테이크를 사주지 않는 편협한 <@U2>!"
        " 악당은 방금 이 너굴맨이 처치했으니 안심하라구!"
    )
    assert said.data["username"] == "너굴맨"
