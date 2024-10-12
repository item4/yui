import pytest

from yui.apps.info.help import help
from yui.box import Box

from ...util import FakeBot


@pytest.mark.asyncio
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
        """Bat

        It's a bat"""

    bot_config.PREFIX = "."
    bot = FakeBot(bot_config, using_box=box)
    bot.add_channel("C1", "general")
    bot.add_user("U1", "item4")
    event = bot.create_message("C1", "U1", "1234.56")

    await help(bot, event, "")

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == (
        f"`{bot_config.PREFIX}dog`: Dog\n`{bot_config.PREFIX}cat`: Cat\n`{bot_config.PREFIX}bat`: Bat"
    )
    assert said.data["thread_ts"] == "1234.56"

    await help(bot, event, "cat")

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert (
        said.data["text"]
        == f"""*{bot_config.PREFIX}cat*
Cat

It's a cat"""
    )
    assert said.data["thread_ts"] == "1234.56"

    await help(bot, event, "none")

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == "그런 명령어는 없어요!"
    assert said.data["thread_ts"] == "1234.56"
