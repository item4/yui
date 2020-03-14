import pytest

from yui.command.helpers import C
from yui.command.helpers import Cs
from yui.command.validators import DM
from yui.command.validators import get_channel_names
from yui.command.validators import not_
from yui.command.validators import only
from yui.types.namespace import name_convert

from ..util import FakeBot


def test_get_channel_names(fx_config):
    fx_config.CHANNELS = {
        'general': 'general',
        'commons': ['general', 'random'],
    }

    bot = FakeBot(fx_config)
    bot.add_user('U1', 'item4')
    bot.add_channel('C1', 'general')
    bot.add_channel('C2', 'random')
    bot.add_channel('C3', 'food')
    bot.add_channel('C4', 'work')
    bot.add_dm('D1', 'U1')
    bot.add_private_channel('G1', 'secret')

    names, dm, fetch_error = get_channel_names(
        [C.general, Cs.commons, name_convert('food'), DM, 'work']
    )

    assert names == {'general', 'random', 'food', 'work'}
    assert dm is True
    assert fetch_error is False

    fetch_error = get_channel_names([C.bug, Cs.bugs])[2]

    assert fetch_error is True


@pytest.mark.asyncio
async def test_only(fx_config):
    fx_config.CHANNELS = {
        'general': 'general',
        'commons': ['general', 'random'],
        'all': '*',
        'no': None,
    }
    bot = FakeBot(fx_config)
    bot.add_user('U1', 'item4')
    bot.add_channel('C1', 'general')
    bot.add_channel('C2', 'random')
    bot.add_channel('C3', 'food')
    bot.add_dm('D1', 'U1')
    bot.add_private_channel('G1', 'secret')

    callback = only('general', 'random')

    event = bot.create_message('C1', 'U1')
    assert await callback(bot, event)
    assert not bot.call_queue

    event = bot.create_message('C2', 'U1')
    assert await callback(bot, event)
    assert not bot.call_queue

    event = bot.create_message('C3', 'U1')
    assert not await callback(bot, event)
    assert not bot.call_queue

    event = bot.create_message('D1', 'U1')
    assert not await callback(bot, event)
    assert not bot.call_queue

    event = bot.create_message('G1', 'U1')
    assert not await callback(bot, event)
    assert not bot.call_queue

    callback = only('general', 'random', error='error!')

    event = bot.create_message('C1', 'U1')
    assert await callback(bot, event)
    assert not bot.call_queue

    event = bot.create_message('C2', 'U1')
    assert await callback(bot, event)
    assert not bot.call_queue

    event = bot.create_message('C3', 'U1')
    assert not await callback(bot, event)
    say = bot.call_queue.pop()
    assert say.method == 'chat.postMessage'
    assert say.data['text'] == 'error!'

    event = bot.create_message('D1', 'U1')
    assert not await callback(bot, event)
    say = bot.call_queue.pop()
    assert say.method == 'chat.postMessage'
    assert say.data['text'] == 'error!'

    event = bot.create_message('G1', 'U1')
    assert not await callback(bot, event)
    say = bot.call_queue.pop()
    assert say.method == 'chat.postMessage'
    assert say.data['text'] == 'error!'

    callback = only('general', 'random', DM)

    event = bot.create_message('C1', 'U1')
    assert await callback(bot, event)
    assert not bot.call_queue

    event = bot.create_message('C2', 'U1')
    assert await callback(bot, event)
    assert not bot.call_queue

    event = bot.create_message('C3', 'U1')
    assert not await callback(bot, event)
    assert not bot.call_queue

    event = bot.create_message('D1', 'U1')
    assert await callback(bot, event)
    assert not bot.call_queue

    event = bot.create_message('G1', 'U1')
    assert not await callback(bot, event)
    assert not bot.call_queue

    callback = only('general', 'random', DM, error='error!')

    event = bot.create_message('C1', 'U1')
    assert await callback(bot, event)
    assert not bot.call_queue

    event = bot.create_message('C2', 'U1')
    assert await callback(bot, event)
    assert not bot.call_queue

    event = bot.create_message('C3', 'U1')
    assert not await callback(bot, event)
    say = bot.call_queue.pop()
    assert say.method == 'chat.postMessage'
    assert say.data['text'] == 'error!'

    event = bot.create_message('D1', 'U1')
    assert await callback(bot, event)
    assert not bot.call_queue

    event = bot.create_message('G1', 'U1')
    assert not await callback(bot, event)
    say = bot.call_queue.pop()
    assert say.method == 'chat.postMessage'
    assert say.data['text'] == 'error!'

    callback = only(C.bug)
    event = bot.create_message('G1', 'U1')
    assert not await callback(bot, event)
    assert not bot.call_queue

    callback = only(Cs.bug)
    event = bot.create_message('G1', 'U1')
    assert not await callback(bot, event)
    assert not bot.call_queue

    callback = only(Cs.all)
    event = bot.create_message('C1', 'U1')
    assert await callback(bot, event)
    assert not bot.call_queue

    callback = only(Cs.no)
    event = bot.create_message('C1', 'U1')
    assert not await callback(bot, event)
    assert not bot.call_queue

    callback = only(Cs.no, error='error!')
    event = bot.create_message('C1', 'U1')
    assert not await callback(bot, event)
    say = bot.call_queue.pop()
    assert say.method == 'chat.postMessage'
    assert say.data['text'] == 'error!'


@pytest.mark.asyncio
async def test_not_(fx_config):
    fx_config.CHANNELS = {
        'general': 'general',
        'commons': ['general', 'random'],
        'all': '*',
        'no': None,
    }

    bot = FakeBot(fx_config)
    bot.add_user('U1', 'item4')
    bot.add_channel('C1', 'general')
    bot.add_channel('C2', 'random')
    bot.add_channel('C3', 'food')
    bot.add_dm('D1', 'U1')
    bot.add_private_channel('G1', 'secret')

    callback = not_('general', 'random')

    event = bot.create_message('C1', 'U1')
    assert not await callback(bot, event)
    assert not bot.call_queue

    event = bot.create_message('C2', 'U1')
    assert not await callback(bot, event)
    assert not bot.call_queue

    event = bot.create_message('C3', 'U1')
    assert await callback(bot, event)
    assert not bot.call_queue

    event = bot.create_message('D1', 'U1')
    assert await callback(bot, event)
    assert not bot.call_queue

    event = bot.create_message('G1', 'U1')
    assert await callback(bot, event)
    assert not bot.call_queue

    callback = not_('general', 'random', error='error!')

    event = bot.create_message('C1', 'U1')
    assert not await callback(bot, event)
    say = bot.call_queue.pop()
    assert say.method == 'chat.postMessage'
    assert say.data['text'] == 'error!'

    event = bot.create_message('C2', 'U1')
    assert not await callback(bot, event)
    say = bot.call_queue.pop()
    assert say.method == 'chat.postMessage'
    assert say.data['text'] == 'error!'

    event = bot.create_message('C3', 'U1')
    assert await callback(bot, event)
    assert not bot.call_queue

    event = bot.create_message('D1', 'U1')
    assert await callback(bot, event)
    assert not bot.call_queue

    event = bot.create_message('G1', 'U1')
    assert await callback(bot, event)
    assert not bot.call_queue

    callback = not_('general', 'random', DM)

    event = bot.create_message('C1', 'U1')
    assert not await callback(bot, event)
    assert not bot.call_queue

    event = bot.create_message('C2', 'U1')
    assert not await callback(bot, event)
    assert not bot.call_queue

    event = bot.create_message('C3', 'U1')
    assert await callback(bot, event)
    assert not bot.call_queue

    event = bot.create_message('D1', 'U1')
    assert not await callback(bot, event)
    assert not bot.call_queue

    event = bot.create_message('G1', 'U1')
    assert await callback(bot, event)
    assert not bot.call_queue

    callback = not_('general', 'random', DM, error='error!')

    event = bot.create_message('C1', 'U1')
    assert not await callback(bot, event)
    say = bot.call_queue.pop()
    assert say.method == 'chat.postMessage'
    assert say.data['text'] == 'error!'

    event = bot.create_message('C2', 'U1')
    assert not await callback(bot, event)
    say = bot.call_queue.pop()
    assert say.method == 'chat.postMessage'
    assert say.data['text'] == 'error!'

    event = bot.create_message('C3', 'U1')
    assert await callback(bot, event)
    assert not bot.call_queue

    event = bot.create_message('D1', 'U1')
    assert not await callback(bot, event)
    say = bot.call_queue.pop()
    assert say.method == 'chat.postMessage'
    assert say.data['text'] == 'error!'

    event = bot.create_message('G1', 'U1')
    assert await callback(bot, event)
    assert not bot.call_queue

    callback = not_(C.bug)
    event = bot.create_message('G1', 'U1')
    assert not await callback(bot, event)
    assert not bot.call_queue

    callback = not_(Cs.bug)
    event = bot.create_message('G1', 'U1')
    assert not await callback(bot, event)
    assert not bot.call_queue

    callback = not_(Cs.all)
    event = bot.create_message('G1', 'U1')
    assert not await callback(bot, event)
    assert not bot.call_queue

    callback = not_(Cs.all, error='error!')
    event = bot.create_message('G1', 'U1')
    assert not await callback(bot, event)
    say = bot.call_queue.pop()
    assert say.method == 'chat.postMessage'
    assert say.data['text'] == 'error!'

    callback = not_(Cs.no)
    event = bot.create_message('G1', 'U1')
    assert await callback(bot, event)
    assert not bot.call_queue
