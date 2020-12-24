import datetime

import pytest

from yui.apps.date.dday import dday


@pytest.mark.asyncio
async def test_dday_command(bot):
    bot.add_channel('C1', 'general')
    bot.add_user('U1', 'item4')
    event = bot.create_message('C1', 'U1')
    jan = datetime.date(2000, 1, 1)
    feb = datetime.date(2000, 2, 1)

    await dday(bot, event, jan, feb)
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == ('2000년 01월 01일로부터 2000년 02월 01일까지 31일 남았어요!')

    await dday(bot, event, feb, jan)
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == ('2000년 01월 01일로부터 2000년 02월 01일까지 31일 지났어요!')
