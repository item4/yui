import pytest

from yui.apps.owner.quit import quit

from ...util import FakeBot


@pytest.mark.asyncio
async def test_quit_command(fx_config):
    fx_config.USERS['owner'] = 'U1'
    bot = FakeBot(fx_config)
    bot.add_channel('C1', 'general')
    bot.add_user('U1', 'kirito')
    bot.add_user('U2', 'PoH')

    event = bot.create_message('C1', 'U1')

    with pytest.raises(SystemExit):
        await quit(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '안녕히 주무세요!'

    event = bot.create_message('C1', 'U2')

    await quit(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '<@PoH> 이 명령어는 아빠만 사용할 수 있어요!'
