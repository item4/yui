import aiohttp.client_exceptions
import pytest
from aiohttp.client_reqrep import ConnectionKey
from yarl import URL

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


@pytest.mark.asyncio()
async def test_add_wrong_url(bot, fx_sess):
    bot.add_channel("C1", "general")
    bot.add_user("U1", "item4")
    r = RSS()

    event = bot.create_message("C1", "U1")

    await r.add(r, bot, event, fx_sess, "wrong url")

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == "`wrong url`은 올바른 URL이 아니에요!"


@pytest.mark.asyncio()
async def test_add_cannot_connect(bot, fx_sess, response_mock):
    response_mock.get(
        URL("https://test.dev/rss.xml"),
        exception=aiohttp.client_exceptions.ClientConnectorError(
            ConnectionKey(
                host="test.dev",
                port=443,
                is_ssl=True,
                ssl=True,
                proxy=None,
                proxy_auth=None,
                proxy_headers_hash=None,
            ),
            OSError(),
        ),
    )
    bot.add_channel("C1", "general")
    bot.add_user("U1", "item4")
    r = RSS()

    event = bot.create_message("C1", "U1")

    await r.add(r, bot, event, fx_sess, "https://test.dev/rss.xml")

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == "`https://test.dev/rss.xml`에 접속할 수 없어요!"


@pytest.mark.asyncio()
async def test_add_empty_body(bot, fx_sess, response_mock):
    response_mock.get(
        URL("https://test.dev/rss.xml"),
        body=b"",
    )
    bot.add_channel("C1", "general")
    bot.add_user("U1", "item4")
    r = RSS()

    event = bot.create_message("C1", "U1")

    await r.add(r, bot, event, fx_sess, "https://test.dev/rss.xml")

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == "`https://test.dev/rss.xml`은 빈 웹페이지에요!"


@pytest.mark.asyncio()
async def test_add_wrong_body(bot, fx_sess, response_mock):
    response_mock.get(
        URL("https://test.dev/rss.xml"),
        body=b"wrong body",
    )
    bot.add_channel("C1", "general")
    bot.add_user("U1", "item4")
    r = RSS()

    event = bot.create_message("C1", "U1")

    await r.add(r, bot, event, fx_sess, "https://test.dev/rss.xml")

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert (
        said.data["text"]
        == "`https://test.dev/rss.xml`은 올바른 RSS 문서가 아니에요!"
    )
