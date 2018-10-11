import pytest

from yui.apps.owner.say import say
from yui.event import create_event

from ...util import FakeBot


@pytest.mark.asyncio
async def test_say_command(fx_config):
    fx_config.OWNER_ID = 'U1'
    bot = FakeBot(fx_config)
    bot.add_channel('C1', 'general')
    test = bot.add_channel('C2', 'test')
    bot.add_user('U1', 'kirito')
    poh = bot.add_user('U2', 'PoH')

    text = '안녕하세요! 하고 유이인 척 하기'

    event = create_event({
        'type': 'message',
        'channel': 'C1',
        'user': 'U1',
    })

    await say(bot, event, None, None, text)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == text

    await say(bot, event, test, None, text)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C2'
    assert said.data['text'] == text

    await say(bot, event, None, poh, text)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'U2'
    assert said.data['text'] == text

    await say(bot, event, test, poh, text)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '`--channel` 옵션과 `--user` 옵션은 동시에 사용할 수 없어요!'
    )

    event = create_event({
        'type': 'message',
        'channel': 'C1',
        'user': 'U2',
    })

    await say(bot, event, None, None, '죽어라!')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '<@PoH> 이 명령어는 아빠만 사용할 수 있어요!'
