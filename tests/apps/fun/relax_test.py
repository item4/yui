import pytest

from yui.apps.fun.relax import relax

from ...util import FakeBot


@pytest.mark.asyncio
async def test_relax_command():
    bot = FakeBot()
    bot.add_channel('C1', 'general')
    bot.add_user('U1', 'item4')
    event = bot.create_message('C1', 'U1')

    await relax(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '유이에게 나쁜 것을 주입하려는 사악한 재벌은 이 너굴맨이 처리했으니 안심하라구!'
    )
    assert said.data['as_user'] == '0'
    assert said.data['username'] == '너굴맨'
