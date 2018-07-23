import pytest

from yui.event import create_event
from yui.handlers.ref import (
    css,
    fetch_css_ref,
    fetch_html_ref,
    fetch_python_ref,
    html,
    python,
)

from ..util import FakeBot


@pytest.mark.asyncio
async def test_css_command(event_loop, fx_sess):
    bot = FakeBot()
    bot.add_channel('C1', 'general')
    event = create_event({
        'type': 'message',
        'channel': 'C1',
    })

    await css(bot, event, fx_sess, 'font-family')
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '아직 레퍼런스 관련 명령어의 실행준비가 덜 되었어요. 잠시만 기다려주세요!'
    )

    await fetch_css_ref(bot, event_loop, fx_sess)

    await css(bot, event, fx_sess, 'font-family')
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        ':css: `font-family` - '
        'https://developer.mozilla.org/en-US/docs/Web/CSS/font-family'
    )

    await css(bot, event, fx_sess, '쀍뗗')
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '비슷한 CSS 관련 요소를 찾지 못하겠어요!'


@pytest.mark.asyncio
async def test_html_command(event_loop, fx_sess):
    bot = FakeBot()
    bot.add_channel('C1', 'general')
    event = create_event({
        'type': 'message',
        'channel': 'C1',
    })

    await html(bot, event, fx_sess, 'section')
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '아직 레퍼런스 관련 명령어의 실행준비가 덜 되었어요. 잠시만 기다려주세요!'
    )

    await fetch_html_ref(bot, event_loop, fx_sess)

    await html(bot, event, fx_sess, 'section')
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        ':html: `<section>` - '
        'https://developer.mozilla.org/en-US/docs/Web/HTML/Element/section'
    )

    await html(bot, event, fx_sess, '쀍뗗')
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '비슷한 HTML Element를 찾지 못하겠어요!'


@pytest.mark.asyncio
async def test_python_command(event_loop, fx_sess):
    bot = FakeBot()
    bot.add_channel('C1', 'general')
    event = create_event({
        'type': 'message',
        'channel': 'C1',
    })

    await python(bot, event, fx_sess, 'builtin function')
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
         '아직 레퍼런스 관련 명령어의 실행준비가 덜 되었어요. 잠시만 기다려주세요!'
    )

    await fetch_python_ref(bot, event_loop, fx_sess)

    await python(bot, event, fx_sess, 'builtin function')
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        ':python: Built-in Functions - '
        'https://docs.python.org/3/library/functions.html'
    )

    await python(bot, event, fx_sess, 're')
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        ':python: re — Regular expression operations - '
        'https://docs.python.org/3/library/re.html'
    )

    await python(bot, event, fx_sess, '쀍뗗')
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '비슷한 Python library를 찾지 못하겠어요!'
