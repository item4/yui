from typing import List

from attrdict import AttrDict

import pytest

from yui.command import (
    Argument,
    C,
    Cs,
    DM,
    Option,
    argument,
    get_channel_names,
    not_,
    only,
    option,
)
from yui.event import create_event
from yui.type import Channel, ChannelFromConfig, ChannelsFromConfig

from .util import FakeBot


def test_c():
    ch = C.general
    assert isinstance(ch, ChannelFromConfig)
    assert ch.key == 'general'

    ch = C['food']
    assert isinstance(ch, ChannelFromConfig)
    assert ch.key == 'food'


def test_cs():
    ch = Cs.tests
    assert isinstance(ch, ChannelsFromConfig)
    assert ch.key == 'tests'

    ch = Cs['commons']
    assert isinstance(ch, ChannelsFromConfig)
    assert ch.key == 'commons'


def test_get_channel_names():
    config = AttrDict({
        'CHANNELS': {
            'general': 'general',
            'commons': ['general', 'random'],
        }
    })
    bot = FakeBot(config)
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
async def test_only():
    config = AttrDict({
        'CHANNELS': {
            'general': 'general',
            'commons': ['general', 'random'],
            'all': '*',
            'no': None,
        }
    })
    bot = FakeBot(config)
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
async def test_not_():
    config = AttrDict({
        'CHANNELS': {
            'general': 'general',
            'commons': ['general', 'random'],
            'all': '*',
            'no': None,
        }
    })
    bot = FakeBot(config)
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


def test_argument_decorator():
    @argument('arg1')
    @argument('arg2', container_cls=list)
    @argument('arg3', nargs=2)
    @argument('arg4', nargs=2, concat=True)
    @argument('arg5', dest='arg_five')
    async def test1():
        pass

    args: List[Argument] = test1.__arguments__
    assert len(args) == 5

    assert args[0].name == 'arg1'
    assert args[0].dest == 'arg1'
    assert args[0].nargs == 1
    assert args[0].transform_func is None
    assert not args[0].concat
    assert args[0].container_cls is None
    assert args[0].type_ is None

    assert args[1].name == 'arg2'
    assert args[1].dest == 'arg2'
    assert args[1].nargs == 1
    assert args[1].transform_func is None
    assert not args[1].concat
    assert args[1].container_cls is None
    assert args[1].type_ is None

    assert args[2].name == 'arg3'
    assert args[2].dest == 'arg3'
    assert args[2].nargs == 2
    assert args[2].transform_func is None
    assert not args[2].concat
    assert args[2].container_cls == tuple
    assert args[2].type_ is None

    assert args[3].name == 'arg4'
    assert args[3].dest == 'arg4'
    assert args[3].nargs == 2
    assert args[3].transform_func is None
    assert args[3].concat
    assert args[3].container_cls is None
    assert args[3].type_ == str

    assert args[4].name == 'arg5'
    assert args[4].dest == 'arg_five'
    assert args[4].nargs == 1
    assert args[4].transform_func is None
    assert not args[4].concat
    assert args[4].container_cls is None
    assert args[4].type_ is None

    with pytest.raises(TypeError) as e:
        @argument('arg1', nargs=-1)
        @argument('arg2', nargs=-1)
        async def test2():
            pass
    assert str(e.value) == 'can not have two nargs<0'


def test_option_decorator():
    @option('-a')
    @option('--bar', '-b')
    @option('-c/C')
    @option('-d', is_flag=True)
    @option('-e', is_flag=True, value=1234)
    async def test1():
        pass

    opts: List[Option] = test1.__options__
    assert len(opts) == 7

    assert opts[0].key == '-a'
    assert opts[0].name == '-a'
    assert opts[0].dest == 'a'
    assert opts[0].value is None
    assert opts[0].default is None
    assert opts[0].nargs == 1
    assert not opts[0].required

    assert opts[1].key == '--bar -b'
    assert opts[1].name == '--bar'
    assert opts[1].dest == 'bar'
    assert opts[1].value is None
    assert opts[1].default is None
    assert opts[1].nargs == 1
    assert not opts[1].required

    assert opts[2].key == '--bar -b'
    assert opts[2].name == '-b'
    assert opts[2].dest == 'bar'
    assert opts[2].value is None
    assert opts[2].default is None
    assert opts[2].nargs == 1
    assert not opts[2].required

    assert opts[3].key == '-c/C'
    assert opts[3].name == '-c'
    assert opts[3].dest == 'c'
    assert opts[3].value is True
    assert opts[3].default is None
    assert opts[3].nargs == 0
    assert not opts[3].required

    assert opts[4].key == '-c/C'
    assert opts[4].name == 'C'
    assert opts[4].dest == 'c'
    assert opts[4].value is False
    assert opts[4].default is None
    assert opts[4].nargs == 0
    assert not opts[4].required

    assert opts[5].key == '-d'
    assert opts[5].name == '-d'
    assert opts[5].dest == 'd'
    assert opts[5].value is True
    assert opts[5].default is None
    assert opts[5].nargs == 0
    assert not opts[5].required

    assert opts[6].key == '-e'
    assert opts[6].name == '-e'
    assert opts[6].dest == 'e'
    assert opts[6].value == 1234
    assert opts[6].default is None
    assert opts[6].nargs == 0
    assert not opts[6].required

    @option('-a', container_cls=list)
    @option('-b', multiple=True)
    @option('-c', nargs=3)
    async def test2():
        pass

    opts: List[Option] = test2.__options__
    assert len(opts) == 3

    assert opts[0].container_cls is None
    assert opts[1].container_cls == tuple
    assert opts[2].container_cls == tuple
