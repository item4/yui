import pytest

from yui.apps.info.help import help
from yui.box import Box

from ...util import FakeBot


@pytest.mark.anyio
async def test_help_command(bot_config):
    box = Box()

    @box.command("dog")
    async def dog(bot, event):
        """Dog

        It's a dog"""

    @box.command("cat")
    async def cat(bot, event):
        """Cat

        It's a cat"""

    @box.command("bat")
    async def bat(bot, event):
        """Bat"""

    bot_config.PREFIX = "."
    bot = FakeBot(bot_config, using_box=box)
    event = bot.create_message(ts="1234.56")

    await help(bot, event, "")

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"] == (
        f"`{bot_config.PREFIX}dog`: Dog\n`{bot_config.PREFIX}cat`: Cat\n`{bot_config.PREFIX}bat`: Bat"
    )
    assert said.data["thread_ts"] == event.ts

    await help(bot, event, "cat")

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert (
        said.data["text"]
        == f"""*{bot_config.PREFIX}cat*
Cat

It's a cat"""
    )
    assert said.data["thread_ts"] == "1234.56"

    await help(bot, event, "bat")

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"] == f"`{bot_config.PREFIX}bat`: Bat"
    assert said.data["thread_ts"] == "1234.56"

    await help(bot, event, "none")

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"] == "그런 명령어는 없어요!"
    assert said.data["thread_ts"] == "1234.56"
