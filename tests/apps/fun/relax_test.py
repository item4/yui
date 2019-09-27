import pytest

from yui.apps.fun.relax import relax

from ...util import FakeBot


@pytest.mark.asyncio
async def test_relax_command():
    bot = FakeBot()
    bot.add_channel('C1', 'general')
    bot.add_user('U1', 'item4')
    event = bot.create_message('C1', 'U1', text='')

    await relax(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '유이에게 나쁜 것을 주입하려는 사악한 J.Valentine은'
        ' 이 너굴맨이 처리했으니 안심하라구!'
    )
    assert said.data['as_user'] == '0'
    assert said.data['username'] == '너굴맨'

    event = bot.create_message('C1', 'U1', text='스테이크')

    await relax(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '사람들에게 스테이크를 사주지 않는 편협한 J.Valentine은'
        ' 이 너굴맨이 처리했으니 안심하라구!'
    )
    assert said.data['as_user'] == '0'
    assert said.data['username'] == '너굴맨'

    event = bot.create_message('C1', 'U1', text='멸망')

    await relax(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '인류문명을 멸망시키려 하는 사악한 J.Valentine은'
        ' 이 너굴맨이 처리했으니 안심하라구!'
    )
    assert said.data['as_user'] == '0'
    assert said.data['username'] == '너굴맨'

    event = bot.create_message('C1', 'U1', text='멸종')

    await relax(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '모든 생명의 멸종을 바람직하게 여기는 잔혹한 J.Valentine은'
        ' 이 너굴맨이 처리했으니 안심하라구!'
    )
    assert said.data['as_user'] == '0'
    assert said.data['username'] == '너굴맨'

    event = bot.create_message('C1', 'U1', text='기업')

    await relax(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '세계를 망치는 국제 대기업들의 흑막 J.Valentine은'
        ' 이 너굴맨이 처리했으니 안심하라구!'
    )
    assert said.data['as_user'] == '0'
    assert said.data['username'] == '너굴맨'

    event = bot.create_message('C1', 'U1', text='회사')

    await relax(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '회사원들이 퇴근하지 못하게 블랙 회사을 종용하는 J.Valentine은'
        ' 이 너굴맨이 처리했으니 안심하라구!'
    )
    assert said.data['as_user'] == '0'
    assert said.data['username'] == '너굴맨'
