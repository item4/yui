import pytest

from yui.event import create_event
from yui.handlers.ref import css, html, php, py

from ..util import FakeBot


@pytest.mark.asyncio
async def test_css_command():
    bot = FakeBot()
    event = create_event({
        'type': 'message',
        'channel': 'C1',
    })

    await css(bot, event, 'font-family')
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        ':css: `font-family` - '
        'https://developer.mozilla.org/en-US/docs/Web/CSS/font-family'
    )

    await css(bot, event, '쀍뗗')
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '비슷한 CSS 관련 요소를 찾지 못하겠어요!'


@pytest.mark.asyncio
async def test_html_command():
    bot = FakeBot()
    event = create_event({
        'type': 'message',
        'channel': 'C1',
    })

    await html(bot, event, 'section')
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        ':html: `<section>` - '
        'https://developer.mozilla.org/en-US/docs/Web/HTML/Element/section'
    )

    await html(bot, event, '쀍뗗')
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '비슷한 HTML Element를 찾지 못하겠어요!'


@pytest.mark.asyncio
async def test_php_command():
    bot = FakeBot()
    event = create_event({
        'type': 'message',
        'channel': 'C1',
    })

    await php(bot, event, 'time')
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'].startswith(':php: `time` - ')

    await php(bot, event, 'mysql_connect')
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'].startswith(':php: `mysql_connect` - ')

    await php(bot, event, 'PDO::exec')
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'].startswith(':php: `PDO::exec` - ')

    await php(bot, event, 'mysqli_stmt_fetch')
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'].startswith(':php: `mysqli_stmt_fetch` - ')

    await php(bot, event, 'mysqli_commit')
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'].startswith(':php: `mysqli_commit` - ')

    await php(bot, event, '쀍뗗')
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '비슷한 PHP 관련 요소를 찾지 못하겠어요!'


@pytest.mark.asyncio
async def test_py_command():
    bot = FakeBot()
    event = create_event({
        'type': 'message',
        'channel': 'C1',
    })

    await py(bot, event, 'builtin function')
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        ':python: Built-in Functions - '
        'https://docs.python.org/3/library/functions.html'
    )

    await py(bot, event, 're')
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        ':python: re — Regular expression operations - '
        'https://docs.python.org/3/library/re.html'
    )

    await py(bot, event, '쀍뗗')
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '비슷한 Python library를 찾지 못하겠어요!'
