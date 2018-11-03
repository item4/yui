import pytest

from yui.apps.fun.hassan import hassan

from ...util import FakeBot


@pytest.mark.asyncio
async def test_hassan_handler():
    bot = FakeBot()
    bot.add_channel('C1', 'general')
    bot.add_user('U1', 'hunj')
    event = bot.create_message('C1', 'U1', text='똑바로 서라 유이')

    assert not await hassan(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '저한테 왜 그러세요 @hunj님?'

    event = bot.create_message('C1', 'U1', text='아무말 대잔치')

    assert await hassan(bot, event)

    assert not bot.call_queue
