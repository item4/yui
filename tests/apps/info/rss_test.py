import aiohttp.client_exceptions
import pytest
from aiohttp.client_reqrep import ConnectionKey
from sqlalchemy.sql.expression import func
from sqlalchemy.sql.expression import select
from yarl import URL

from yui.apps.info.rss.commands import RSS
from yui.apps.info.rss.models import RSSFeedURL
from yui.utils.datetime import datetime


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


@pytest.mark.asyncio
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


@pytest.mark.asyncio
async def test_add_wrong_url(bot, fx_sess):
    bot.add_channel("C1", "general")
    bot.add_user("U1", "item4")
    r = RSS()

    event = bot.create_message("C1", "U1")

    await r.add(bot, event, fx_sess, "wrong url")

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == "`wrong url`은 올바른 URL이 아니에요!"


@pytest.mark.asyncio
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

    await r.add(bot, event, fx_sess, "https://test.dev/rss.xml")

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == "`https://test.dev/rss.xml`에 접속할 수 없어요!"


@pytest.mark.asyncio
async def test_add_empty_body(bot, fx_sess, response_mock):
    response_mock.get(
        URL("https://test.dev/rss.xml"),
        body=b"",
    )
    bot.add_channel("C1", "general")
    bot.add_user("U1", "item4")
    r = RSS()

    event = bot.create_message("C1", "U1")

    await r.add(bot, event, fx_sess, "https://test.dev/rss.xml")

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == "`https://test.dev/rss.xml`은 빈 웹페이지에요!"


@pytest.mark.asyncio
async def test_add_wrong_body(bot, fx_sess, response_mock):
    response_mock.get(
        URL("https://test.dev/rss.xml"),
        body=b"wrong body",
    )
    bot.add_channel("C1", "general")
    bot.add_user("U1", "item4")
    r = RSS()

    event = bot.create_message("C1", "U1")

    await r.add(bot, event, fx_sess, "https://test.dev/rss.xml")

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert (
        said.data["text"]
        == "`https://test.dev/rss.xml`은 올바른 RSS 문서가 아니에요!"
    )


@pytest.mark.asyncio
async def test_add_success(bot, fx_sess, response_mock):
    response_mock.get(
        URL("https://test.dev/rss.xml"),
        body="""\
<rss xmlns:c="http://purl.org/rss/1.0/modules/content/" version="2.0">
<channel>
<title>item4 dev story</title>
<link>https://item4.blog</link>
<description>한국인 소프트웨어 엔지니어 item4의 기술 블로그</description>
<lastBuildDate>Sun, 22 Mar 2020 09:09:00 GMT</lastBuildDate>
<docs>https://validator.w3.org/feed/docs/rss2.html</docs>
<generator>item4 Next.js blog Powered by Feed for nodejs</generator>
<language>ko-KR</language>
<image>
<title>item4 dev story</title>
<url>https://item4.blog/item4.png</url>
<link>https://item4.blog</link>
</image>
<copyright>CCL 4.0 BY-SA</copyright>
<item>
<title>
<![CDATA[ drf-yasg-examples ]]>
</title>
<link>https://item4.blog/2020-03-22/drf-yasg-examples/</link>
<guid>https://item4.blog/2020-03-22/drf-yasg-examples/</guid>
<pubDate>Sun, 22 Mar 2020 09:09:00 GMT</pubDate>
<description>
<![CDATA[ Introduce drf-yasg-examples Package ]]>
</description>
<c:encoded>
<![CDATA[ Introduce drf-yasg-examples Package ]]>
</c:encoded>
<category domain="https://item4.blog/tags/Python/">Python</category>
<category domain="https://item4.blog/tags/Django/">Django</category>
<category domain="https://item4.blog/tags/django-rest-framework/">django-rest-framework</category>
<category domain="https://item4.blog/tags/drf-yasg/">drf-yasg</category>
<category domain="https://item4.blog/tags/Swagger/">Swagger</category>
<category domain="https://item4.blog/tags/openapi/">openapi</category>
<category domain="https://item4.blog/tags/API/">API</category>
<category domain="https://item4.blog/tags/Documentation/">Documentation</category>
<category domain="https://item4.blog/tags/drf-yasg-examples/">drf-yasg-examples</category>
</item>
</channel>
</rss>
""",
    )
    bot.add_channel("C1", "general")
    bot.add_user("U1", "item4")
    r = RSS()

    event = bot.create_message("C1", "U1")

    await r.add(bot, event, fx_sess, "https://test.dev/rss.xml")

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert (
        said.data["text"]
        == "<#C1> 채널에서 `https://test.dev/rss.xml`을 구독하기 시작했어요!"
    )
    assert (
        await fx_sess.scalar(
            select(func.count(RSSFeedURL.id)).where(
                RSSFeedURL.url == "https://test.dev/rss.xml",
            ),
        )
        == 1
    )
    rss = await fx_sess.scalar(
        select(RSSFeedURL).where(RSSFeedURL.url == "https://test.dev/rss.xml"),
    )
    assert rss.channel == "C1"
    assert rss.updated_at == datetime(2020, 3, 22, 18, 9)


@pytest.mark.asyncio
async def test_list_no_item(bot, fx_sess):
    bot.add_channel("C1", "general")
    bot.add_user("U1", "item4")
    r = RSS()

    event = bot.create_message("C1", "U1")

    await r.list(bot, event, fx_sess)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == "<#C1> 채널에서 구독중인 RSS가 없어요!"


@pytest.mark.asyncio
async def test_list_fine(bot, fx_sess):
    bot.add_channel("C1", "general")
    bot.add_user("U1", "item4")
    r = RSS()

    event = bot.create_message("C1", "U1")

    feed1 = RSSFeedURL()
    feed1.channel = "C1"
    feed1.url = "https://test.dev/rss.xml"
    feed1.updated_at = datetime(2020, 3, 22, 18, 9)
    feed2 = RSSFeedURL()
    feed2.channel = "C1"
    feed2.url = "https://test.dev/rss2.xml"
    feed2.updated_at = datetime(2020, 3, 22, 10, 45)
    async with fx_sess.begin():
        fx_sess.add(feed1)
        fx_sess.add(feed2)
        fx_sess.commit()

    await r.list(bot, event, fx_sess)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert (
        said.data["text"]
        == f"""\
<#C1> 채널에서 구독중인 RSS 목록은 다음과 같아요!
```
{feed1.id} - {feed1.url}
{feed2.id} - {feed2.url}
```"""
    )
