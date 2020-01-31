import pytest

from yui.apps.fun.code import code_review, write_code_review
from yui.utils import json

from ...util import FakeBot


@pytest.mark.asyncio
async def test_write_code_review():
    bot = FakeBot()
    bot.add_channel('C1', 'general')
    bot.add_user('U1', 'item4')

    event = bot.create_message('C1', 'U1', text='램지 코드 리뷰')
    await write_code_review(bot, event, seed=100)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'

    assert said.data['as_user'] == '0'

    attachments = json.loads(said.data['attachments'])

    assert len(attachments) == 1
    assert attachments[0]['fallback'] == attachments[0]['image_url'] == \
        'https://i.imgur.com/btkBRvc.png'


@pytest.mark.asyncio
async def test_code_review():
    bot = FakeBot()
    bot.add_channel('C1', 'general')
    bot.add_user('U1', 'item4')

    event = bot.create_message('C1', 'U1', text='코드 리뷰')

    assert await code_review(bot, event)

    assert not bot.call_queue

    event = bot.create_message('C1', 'U1', text='램지 코드 리뷰')

    assert not await code_review(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert len(json.loads(said.data['attachments'])) == 1
    assert said.data['as_user'] == '0'

    event = bot.create_message('C1', 'U1', text='램지 코드 리뷰')

    assert await code_review(bot, event)
