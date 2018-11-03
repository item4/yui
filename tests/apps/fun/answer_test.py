import pytest

from yui.apps.fun.answer import RESPONSES, magic_conch

from ...util import FakeBot


@pytest.mark.asyncio
async def test_magic_conch():
    bot = FakeBot()
    bot.add_channel('C1', 'general')
    bot.add_user('U1', 'item4')

    event = bot.create_message('C1', 'U1', text='마법의 유이님')

    assert await magic_conch(bot, event)

    assert not bot.call_queue

    event = bot.create_message('C1', 'U1', text='마법의 소라고둥님')

    assert not await magic_conch(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] in RESPONSES

    event = bot.create_message('C1', 'U1', text='마법 소라고동')

    assert not await magic_conch(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] in RESPONSES
