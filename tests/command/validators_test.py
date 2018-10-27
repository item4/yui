import pytest

from yui.command.helpers import C, Cs
from yui.command.validators import DM, get_channel_names, not_, only
from yui.event import create_event
from yui.types.namespace.linked import Channel

from ..util import FakeBot


def test_get_channel_names(fx_config):
    fx_config.CHANNELS = {
        'general': 'general',
        'commons': ['general', 'random'],
    }

    bot = FakeBot(fx_config)
    bot.add_channel('C1', 'general')
    bot.add_channel('C2', 'random')
    bot.add_channel('C3', 'food')
    bot.add_channel('C4', 'work')
    bot.add_dm('D1', 'U1')
    bot.add_private_channel('G1', 'secret')

    names, dm, fetch_error = get_channel_names([
        C.general,
        Cs.commons,
        Channel.from_name('food'),
        DM,
        'work',
    ])

    assert names == {'general', 'random', 'food', 'work'}
    assert dm is True
    assert fetch_error is False

    fetch_error = get_channel_names([
        C.bug,
        Cs.bugs,
    ])[2]

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
    bot.add_channel('C1', 'general')
    bot.add_channel('C2', 'random')
    bot.add_channel('C3', 'food')
    bot.add_dm('D1', 'U1')
    bot.add_private_channel('G1', 'secret')

    callback = only('general', 'random')

    event = create_event(dict(type='message', channel='C1'))
    assert await callback(bot, event)
    assert not bot.call_queue

    event = create_event(dict(type='message', channel='C2'))
    assert await callback(bot, event)
    assert not bot.call_queue

    event = create_event(dict(type='message', channel='C3'))
    assert not await callback(bot, event)
    assert not bot.call_queue

    event = create_event(dict(type='message', channel='D1'))
    assert not await callback(bot, event)
    assert not bot.call_queue

    event = create_event(dict(type='message', channel='G1'))
    assert not await callback(bot, event)
    assert not bot.call_queue

    callback = only('general', 'random', error='error!')

    event = create_event(dict(type='message', channel='C1'))
    assert await callback(bot, event)
    assert not bot.call_queue

    event = create_event(dict(type='message', channel='C2'))
    assert await callback(bot, event)
    assert not bot.call_queue

    event = create_event(dict(type='message', channel='C3'))
    assert not await callback(bot, event)
    say = bot.call_queue.pop()
    assert say.method == 'chat.postMessage'
    assert say.data['text'] == 'error!'

    event = create_event(dict(type='message', channel='D1'))
    assert not await callback(bot, event)
    say = bot.call_queue.pop()
    assert say.method == 'chat.postMessage'
    assert say.data['text'] == 'error!'

    event = create_event(dict(type='message', channel='G1'))
    assert not await callback(bot, event)
    say = bot.call_queue.pop()
    assert say.method == 'chat.postMessage'
    assert say.data['text'] == 'error!'

    callback = only('general', 'random', DM)

    event = create_event(dict(type='message', channel='C1'))
    assert await callback(bot, event)
    assert not bot.call_queue

    event = create_event(dict(type='message', channel='C2'))
    assert await callback(bot, event)
    assert not bot.call_queue

    event = create_event(dict(type='message', channel='C3'))
    assert not await callback(bot, event)
    assert not bot.call_queue

    event = create_event(dict(type='message', channel='D1'))
    assert await callback(bot, event)
    assert not bot.call_queue

    event = create_event(dict(type='message', channel='G1'))
    assert not await callback(bot, event)
    assert not bot.call_queue

    callback = only('general', 'random', DM, error='error!')

    event = create_event(dict(type='message', channel='C1'))
    assert await callback(bot, event)
    assert not bot.call_queue

    event = create_event(dict(type='message', channel='C2'))
    assert await callback(bot, event)
    assert not bot.call_queue

    event = create_event(dict(type='message', channel='C3'))
    assert not await callback(bot, event)
    say = bot.call_queue.pop()
    assert say.method == 'chat.postMessage'
    assert say.data['text'] == 'error!'

    event = create_event(dict(type='message', channel='D1'))
    assert await callback(bot, event)
    assert not bot.call_queue

    event = create_event(dict(type='message', channel='G1'))
    assert not await callback(bot, event)
    say = bot.call_queue.pop()
    assert say.method == 'chat.postMessage'
    assert say.data['text'] == 'error!'

    callback = only(C.bug)
    event = create_event(dict(type='message', channel='G1'))
    assert not await callback(bot, event)
    assert not bot.call_queue

    callback = only(Cs.bug)
    event = create_event(dict(type='message', channel='G1'))
    assert not await callback(bot, event)
    assert not bot.call_queue

    callback = only(Cs.all)
    event = create_event(dict(type='message', channel='C1'))
    assert await callback(bot, event)
    assert not bot.call_queue

    callback = only(Cs.no)
    event = create_event(dict(type='message', channel='C1'))
    assert not await callback(bot, event)
    assert not bot.call_queue

    callback = only(Cs.no, error='error!')
    event = create_event(dict(type='message', channel='C1'))
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
    bot.add_channel('C1', 'general')
    bot.add_channel('C2', 'random')
    bot.add_channel('C3', 'food')
    bot.add_dm('D1', 'U1')
    bot.add_private_channel('G1', 'secret')

    callback = not_('general', 'random')

    event = create_event(dict(type='message', channel='C1'))
    assert not await callback(bot, event)
    assert not bot.call_queue

    event = create_event(dict(type='message', channel='C2'))
    assert not await callback(bot, event)
    assert not bot.call_queue

    event = create_event(dict(type='message', channel='C3'))
    assert await callback(bot, event)
    assert not bot.call_queue

    event = create_event(dict(type='message', channel='D1'))
    assert await callback(bot, event)
    assert not bot.call_queue

    event = create_event(dict(type='message', channel='G1'))
    assert await callback(bot, event)
    assert not bot.call_queue

    callback = not_('general', 'random', error='error!')

    event = create_event(dict(type='message', channel='C1'))
    assert not await callback(bot, event)
    say = bot.call_queue.pop()
    assert say.method == 'chat.postMessage'
    assert say.data['text'] == 'error!'

    event = create_event(dict(type='message', channel='C2'))
    assert not await callback(bot, event)
    say = bot.call_queue.pop()
    assert say.method == 'chat.postMessage'
    assert say.data['text'] == 'error!'

    event = create_event(dict(type='message', channel='C3'))
    assert await callback(bot, event)
    assert not bot.call_queue

    event = create_event(dict(type='message', channel='D1'))
    assert await callback(bot, event)
    assert not bot.call_queue

    event = create_event(dict(type='message', channel='G1'))
    assert await callback(bot, event)
    assert not bot.call_queue

    callback = not_('general', 'random', DM)

    event = create_event(dict(type='message', channel='C1'))
    assert not await callback(bot, event)
    assert not bot.call_queue

    event = create_event(dict(type='message', channel='C2'))
    assert not await callback(bot, event)
    assert not bot.call_queue

    event = create_event(dict(type='message', channel='C3'))
    assert await callback(bot, event)
    assert not bot.call_queue

    event = create_event(dict(type='message', channel='D1'))
    assert not await callback(bot, event)
    assert not bot.call_queue

    event = create_event(dict(type='message', channel='G1'))
    assert await callback(bot, event)
    assert not bot.call_queue

    callback = not_('general', 'random', DM, error='error!')

    event = create_event(dict(type='message', channel='C1'))
    assert not await callback(bot, event)
    say = bot.call_queue.pop()
    assert say.method == 'chat.postMessage'
    assert say.data['text'] == 'error!'

    event = create_event(dict(type='message', channel='C2'))
    assert not await callback(bot, event)
    say = bot.call_queue.pop()
    assert say.method == 'chat.postMessage'
    assert say.data['text'] == 'error!'

    event = create_event(dict(type='message', channel='C3'))
    assert await callback(bot, event)
    assert not bot.call_queue

    event = create_event(dict(type='message', channel='D1'))
    assert not await callback(bot, event)
    say = bot.call_queue.pop()
    assert say.method == 'chat.postMessage'
    assert say.data['text'] == 'error!'

    event = create_event(dict(type='message', channel='G1'))
    assert await callback(bot, event)
    assert not bot.call_queue

    callback = not_(C.bug)
    event = create_event(dict(type='message', channel='G1'))
    assert not await callback(bot, event)
    assert not bot.call_queue

    callback = not_(Cs.bug)
    event = create_event(dict(type='message', channel='G1'))
    assert not await callback(bot, event)
    assert not bot.call_queue

    callback = not_(Cs.all)
    event = create_event(dict(type='message', channel='G1'))
    assert not await callback(bot, event)
    assert not bot.call_queue

    callback = not_(Cs.all, error='error!')
    event = create_event(dict(type='message', channel='G1'))
    assert not await callback(bot, event)
    say = bot.call_queue.pop()
    assert say.method == 'chat.postMessage'
    assert say.data['text'] == 'error!'

    callback = not_(Cs.no)
    event = create_event(dict(type='message', channel='G1'))
    assert await callback(bot, event)
    assert not bot.call_queue
