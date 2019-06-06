import pytest

from yui.apps.owner.say import say
from yui.types.slack.response import APIResponse

from ...util import FakeBot


@pytest.mark.asyncio
async def test_say_command(fx_config):
    fx_config.USERS['owner'] = 'U1'
    bot = FakeBot(fx_config)
    bot.add_channel('C1', 'general')
    test = bot.add_channel('C2', 'test')
    bot.add_user('U1', 'kirito')
    poh = bot.add_user('U2', 'PoH')

    @bot.response('im.open')
    def im_open(data):
        return APIResponse(
            body={
                'ok': True,
                'channel': {
                    'id': data['user'].replace('U', 'D'),
                },
            },
            status=200,
            headers={},
        )

    text = '안녕하세요! 하고 유이인 척 하기'

    event = bot.create_message('C1', 'U1')

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

    imopen = bot.call_queue.pop(0)
    assert imopen.method == 'im.open'
    assert imopen.data['user'] == 'U2'
    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'D2'
    assert said.data['text'] == text

    await say(bot, event, test, poh, text)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '`--channel` 옵션과 `--user` 옵션은 동시에 사용할 수 없어요!'
    )

    event = bot.create_message('C1', 'U2')

    await say(bot, event, None, None, '죽어라!')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '<@PoH> 이 명령어는 아빠만 사용할 수 있어요!'
