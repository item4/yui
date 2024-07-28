import pytest

from yui.apps.info.rss.commands import RSS


def test_class():
    r = RSS()
    assert r.name == "rss"
    assert r.route_list


def test_get_short_help():
    r = RSS()
    assert r.get_short_help(".")


def test_get_full_help():
    r = RSS()
    assert r.get_full_help(".")


@pytest.mark.asyncio()
async def test_fallback(bot):
    bot.add_channel("C1", "general")
    bot.add_user("U1", "item4")
    r = RSS()

    event = bot.create_message("C1", "U1")

    await r.fallback(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == f"Usage: `{bot.config.PREFIX}help rss`"
