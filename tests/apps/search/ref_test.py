from datetime import timedelta

import pytest
import pytest_asyncio
from more_itertools import flatten

from yui.apps.search.ref import css
from yui.apps.search.ref import fetch_all_ref
from yui.apps.search.ref import fetch_css_ref
from yui.apps.search.ref import fetch_html_ref
from yui.apps.search.ref import fetch_python_ref
from yui.apps.search.ref import html
from yui.apps.search.ref import on_start
from yui.apps.search.ref import python
from yui.apps.search.ref import refresh

from ...util import FakeBot
from ...util import assert_crontab_match
from ...util import assert_crontab_spec


@pytest_asyncio.fixture()
async def bot(cache) -> FakeBot:
    return FakeBot(cache=cache)


@pytest.mark.asyncio
async def test_fetch_all_ref(bot: FakeBot):
    async with bot.begin():
        html_data = await bot.cache.get("REF_HTML")
        assert html_data is None

        css_data = await bot.cache.get("REF_CSS")
        assert css_data is None

        python_data = await bot.cache.get("REF_PYTHON")
        assert python_data is None

        await fetch_all_ref(bot)

        html_data = await bot.cache.get("REF_HTML")
        assert isinstance(html_data, list)
        assert html_data

        css_data = await bot.cache.get("REF_CSS")
        assert isinstance(css_data, list)
        assert css_data

        python_data = await bot.cache.get("REF_PYTHON")
        assert isinstance(python_data, list)
        assert python_data


@pytest.mark.asyncio
async def test_on_start(bot: FakeBot, monkeypatch):
    async def fake_fetch(bot_):
        assert bot is bot_

    monkeypatch.setattr(
        "yui.apps.search.ref.fetch_all_ref",
        fake_fetch,
    )
    async with bot.begin():
        assert await on_start(bot)


@pytest.mark.asyncio
async def test_refresh(bot: FakeBot, monkeypatch):
    async def fake_fetch(bot_):
        assert bot is bot_

    monkeypatch.setattr(
        "yui.apps.search.ref.fetch_all_ref",
        fake_fetch,
    )
    async with bot.begin():
        await refresh(bot)


def test_refresh_spec():
    assert_crontab_spec(refresh)


@pytest.mark.parametrize(
    ("delta", "result"),
    flatten(
        [
            (timedelta(days=x, hours=0), False),
            (timedelta(days=x, hours=2), False),
            (timedelta(days=x, hours=3), True),
            (timedelta(days=x, hours=3, minutes=30), False),
            (timedelta(days=x, hours=4), False),
        ]
        for x in range(7)
    ),
)
def test_refresh_match(sunday, delta, result):
    assert_crontab_match(refresh, sunday + delta, expected=result)


@pytest.mark.asyncio
async def test_css_command(bot: FakeBot):
    event = bot.create_message()

    async with bot.begin():
        await css(bot, event, "font-family")
        said = bot.call_queue.pop()
        assert said.method == "chat.postMessage"
        assert isinstance(said.data, dict)
        assert said.data["channel"] == event.channel
        assert (
            said.data["text"]
            == "아직 레퍼런스 관련 명령어의 실행준비가 덜 되었어요. 잠시만 기다려주세요!"
        )

        await fetch_css_ref(bot)

        await css(bot, event, "font-family")
        said = bot.call_queue.pop()
        assert said.method == "chat.postMessage"
        assert isinstance(said.data, dict)
        assert said.data["channel"] == event.channel
        assert (
            said.data["text"] == "CSS `font-family` - "
            "https://developer.mozilla.org/en-US/docs/Web/CSS/font-family"
        )

        await css(bot, event, "쀍뗗")
        said = bot.call_queue.pop()
        assert said.method == "chat.postMessage"
        assert isinstance(said.data, dict)
        assert said.data["channel"] == event.channel
        assert said.data["text"] == "비슷한 CSS 관련 요소를 찾지 못하겠어요!"


@pytest.mark.asyncio
async def test_html_command(bot: FakeBot):
    event = bot.create_message()

    async with bot.begin():
        await html(bot, event, "section")
        said = bot.call_queue.pop()
        assert said.method == "chat.postMessage"
        assert isinstance(said.data, dict)
        assert said.data["channel"] == event.channel
        assert (
            said.data["text"]
            == "아직 레퍼런스 관련 명령어의 실행준비가 덜 되었어요. 잠시만 기다려주세요!"
        )

        await fetch_html_ref(bot)

        await html(bot, event, "section")
        said = bot.call_queue.pop()
        assert said.method == "chat.postMessage"
        assert isinstance(said.data, dict)
        assert said.data["channel"] == event.channel
        assert (
            said.data["text"] == "HTML `<section>` - "
            "https://developer.mozilla.org/en-US/docs/Web/HTML/Element/section"
        )

        await html(bot, event, "쀍뗗")
        said = bot.call_queue.pop()
        assert said.method == "chat.postMessage"
        assert isinstance(said.data, dict)
        assert said.data["channel"] == event.channel
        assert said.data["text"] == "비슷한 HTML Element를 찾지 못하겠어요!"


@pytest.mark.asyncio
async def test_python_command(bot: FakeBot):
    event = bot.create_message()

    async with bot.begin():
        await python(bot, event, "builtin function")
        said = bot.call_queue.pop()
        assert said.method == "chat.postMessage"
        assert isinstance(said.data, dict)
        assert said.data["channel"] == event.channel
        assert (
            said.data["text"]
            == "아직 레퍼런스 관련 명령어의 실행준비가 덜 되었어요. 잠시만 기다려주세요!"
        )

        await fetch_python_ref(bot)

        await python(bot, event, "builtin function")
        said = bot.call_queue.pop()
        assert said.method == "chat.postMessage"
        assert isinstance(said.data, dict)
        assert said.data["channel"] == event.channel
        assert (
            said.data["text"] == "Python Built-in Functions - "
            "https://docs.python.org/3/library/functions.html"
        )

        await python(bot, event, "re")
        said = bot.call_queue.pop()
        assert said.method == "chat.postMessage"
        assert isinstance(said.data, dict)
        assert said.data["channel"] == event.channel
        assert (
            said.data["text"] == "Python re — Regular expression operations - "
            "https://docs.python.org/3/library/re.html"
        )

        await python(bot, event, "쀍뗗")
        said = bot.call_queue.pop()
        assert said.method == "chat.postMessage"
        assert isinstance(said.data, dict)
        assert said.data["channel"] == event.channel
        assert said.data["text"] == "비슷한 Python library를 찾지 못하겠어요!"
