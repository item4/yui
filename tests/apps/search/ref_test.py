import asyncio

import pytest
import pytest_asyncio

from yui.apps.search.ref import css
from yui.apps.search.ref import fetch_css_ref
from yui.apps.search.ref import fetch_html_ref
from yui.apps.search.ref import fetch_python_ref
from yui.apps.search.ref import html
from yui.apps.search.ref import python

from ...util import FakeBot


@pytest_asyncio.fixture()
async def bot(cache) -> FakeBot:
    return FakeBot(loop=asyncio.get_running_loop(), cache=cache)


@pytest.mark.asyncio()
async def test_css_command(bot: FakeBot):
    bot.add_channel("C1", "general")
    bot.add_user("U1", "item4")
    event = bot.create_message("C1", "U1")

    async with bot.begin():
        await css(bot, event, "font-family")
        said = bot.call_queue.pop()
        assert said.method == "chat.postMessage"
        assert isinstance(said.data, dict)
        assert said.data["channel"] == "C1"
        assert (
            said.data["text"]
            == "아직 레퍼런스 관련 명령어의 실행준비가 덜 되었어요. 잠시만 기다려주세요!"
        )

        await fetch_css_ref(bot)

        await css(bot, event, "font-family")
        said = bot.call_queue.pop()
        assert said.method == "chat.postMessage"
        assert isinstance(said.data, dict)
        assert said.data["channel"] == "C1"
        assert (
            said.data["text"] == "CSS `font-family` - "
            "https://developer.mozilla.org/en-US/docs/Web/CSS/font-family"
        )

        await css(bot, event, "쀍뗗")
        said = bot.call_queue.pop()
        assert said.method == "chat.postMessage"
        assert isinstance(said.data, dict)
        assert said.data["channel"] == "C1"
        assert said.data["text"] == "비슷한 CSS 관련 요소를 찾지 못하겠어요!"


@pytest.mark.asyncio()
async def test_html_command(bot: FakeBot):
    bot.add_channel("C1", "general")
    bot.add_user("U1", "item4")
    event = bot.create_message("C1", "U1")

    async with bot.begin():
        await html(bot, event, "section")
        said = bot.call_queue.pop()
        assert said.method == "chat.postMessage"
        assert isinstance(said.data, dict)
        assert said.data["channel"] == "C1"
        assert (
            said.data["text"]
            == "아직 레퍼런스 관련 명령어의 실행준비가 덜 되었어요. 잠시만 기다려주세요!"
        )

        await fetch_html_ref(bot)

        await html(bot, event, "section")
        said = bot.call_queue.pop()
        assert said.method == "chat.postMessage"
        assert isinstance(said.data, dict)
        assert said.data["channel"] == "C1"
        assert (
            said.data["text"] == "HTML `<section>` - "
            "https://developer.mozilla.org/en-US/docs/Web/HTML/Element/section"
        )

        await html(bot, event, "쀍뗗")
        said = bot.call_queue.pop()
        assert said.method == "chat.postMessage"
        assert isinstance(said.data, dict)
        assert said.data["channel"] == "C1"
        assert said.data["text"] == "비슷한 HTML Element를 찾지 못하겠어요!"


@pytest.mark.asyncio()
async def test_python_command(bot: FakeBot):
    bot.add_channel("C1", "general")
    bot.add_user("U1", "item4")
    event = bot.create_message("C1", "U1")

    async with bot.begin():
        await python(bot, event, "builtin function")
        said = bot.call_queue.pop()
        assert said.method == "chat.postMessage"
        assert isinstance(said.data, dict)
        assert said.data["channel"] == "C1"
        assert (
            said.data["text"]
            == "아직 레퍼런스 관련 명령어의 실행준비가 덜 되었어요. 잠시만 기다려주세요!"
        )

        await fetch_python_ref(bot)

        await python(bot, event, "builtin function")
        said = bot.call_queue.pop()
        assert said.method == "chat.postMessage"
        assert isinstance(said.data, dict)
        assert said.data["channel"] == "C1"
        assert (
            said.data["text"] == "Python Built-in Functions - "
            "https://docs.python.org/3/library/functions.html"
        )

        await python(bot, event, "re")
        said = bot.call_queue.pop()
        assert said.method == "chat.postMessage"
        assert isinstance(said.data, dict)
        assert said.data["channel"] == "C1"
        assert (
            said.data["text"] == "Python re — Regular expression operations - "
            "https://docs.python.org/3/library/re.html"
        )

        await python(bot, event, "쀍뗗")
        said = bot.call_queue.pop()
        assert said.method == "chat.postMessage"
        assert isinstance(said.data, dict)
        assert said.data["channel"] == "C1"
        assert said.data["text"] == "비슷한 Python library를 찾지 못하겠어요!"
