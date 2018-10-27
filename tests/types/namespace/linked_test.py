import pytest

from yui.exceptions import AllChannelsError, NoChannelsError
from yui.types.namespace.linked import (
    ChannelFromConfig,
    ChannelsFromConfig,
    DirectMessageChannel,
    FromChannelID,
    FromUserID,
    PrivateChannel,
    PublicChannel,
    UnknownChannel,
    UnknownUser,
    User,
)

from ...util import FakeBot


def test_from_channel_id(fx_config):
    fx_config.CHANNELS = {
        'main': 'general',
        'commons': ['general', 'random'],
        'no': 'no',
        'nos': ['no'],
    }
    bot = FakeBot(fx_config)
    bot.add_channel('C1', 'general')
    bot.add_channel('C2', 'random')
    bot.add_channel('C3', 'food')
    bot.add_dm('D1', 'U1')
    bot.add_private_channel('G1', 'secret')

    channel = FromChannelID.from_id('C1')
    assert isinstance(channel, PublicChannel)
    assert channel.id == 'C1'
    assert channel.name == 'general'

    dm = FromChannelID.from_id('D1')
    assert isinstance(dm, DirectMessageChannel)
    assert dm.id == 'D1'
    assert dm.user == 'U1'

    group = FromChannelID.from_id('G1')
    assert isinstance(group, PrivateChannel)
    assert group.id == 'G1'
    assert group.name == 'secret'

    unknown = FromChannelID.from_id('G2')
    assert isinstance(unknown, UnknownChannel)
    assert unknown.id == 'G2'

    with pytest.raises(KeyError):
        FromChannelID.from_id('G2', raise_error=True)

    channel = FromChannelID.from_name('general')
    assert isinstance(channel, PublicChannel)
    assert channel.id == 'C1'
    assert channel.name == 'general'

    group = FromChannelID.from_name('secret')
    assert isinstance(group, PrivateChannel)
    assert group.id == 'G1'
    assert group.name == 'secret'

    with pytest.raises(KeyError):
        FromChannelID.from_name('doge')

    main = FromChannelID.from_config('main')
    assert isinstance(main, PublicChannel)
    assert main.id == 'C1'
    assert main.name == 'general'

    with pytest.raises(ValueError):
        FromChannelID.from_config('commons')

    with pytest.raises(KeyError):
        FromChannelID.from_config('doge')

    with pytest.raises(KeyError):
        FromChannelID.from_config('no')

    commons = FromChannelID.from_config_list('commons')
    assert len(commons) == 2
    assert isinstance(commons[0], PublicChannel)
    assert commons[0].id == 'C1'
    assert commons[0].name == 'general'
    assert isinstance(commons[1], PublicChannel)
    assert commons[1].id == 'C2'
    assert commons[1].name == 'random'

    with pytest.raises(ValueError):
        FromChannelID.from_config_list('main')

    with pytest.raises(KeyError):
        FromChannelID.from_config_list('doge')

    with pytest.raises(KeyError):
        FromChannelID.from_config_list('nos')


def test_from_user_id():
    bot = FakeBot()
    bot.add_user('U1', 'kirito')
    bot.add_user('U2', 'asuna')

    kirito = FromUserID.from_id('U1')
    assert isinstance(kirito, User)
    assert kirito.id == 'U1'
    assert kirito.name == 'kirito'

    asuna = FromUserID.from_id('U2')
    assert isinstance(asuna, User)
    assert asuna.id == 'U2'
    assert asuna.name == 'asuna'

    unknown = FromUserID.from_id('U3')
    assert isinstance(unknown, UnknownUser)
    assert unknown.id == 'U3'

    with pytest.raises(KeyError):
        FromUserID.from_id('U3', raise_error=True)

    kirito = FromUserID.from_name('kirito')
    assert isinstance(kirito, User)
    assert kirito.id == 'U1'
    assert kirito.name == 'kirito'

    asuna = FromUserID.from_name('asuna')
    assert isinstance(asuna, User)
    assert asuna.id == 'U2'
    assert asuna.name == 'asuna'

    with pytest.raises(KeyError):
        FromUserID.from_name('yuuna')


def test_channel_from_config(fx_config):
    fx_config.CHANNELS = {
        'main': 'general',
        'commons': ['general', 'random'],
    }
    bot = FakeBot(fx_config)
    bot.add_channel('C1', 'general')
    bot.add_channel('C2', 'random')
    bot.add_channel('C3', 'food')
    bot.add_dm('D1', 'U1')
    bot.add_private_channel('G1', 'secret')

    c = ChannelFromConfig('main')
    assert c.key == 'main'

    c_get = c.get()
    assert c_get.name == 'general'
    assert c_get.id == 'C1'

    with pytest.raises(KeyError):
        ChannelFromConfig('no').get()


def test_channels_from_config(fx_config):
    fx_config.CHANNELS = {
        'main': 'general',
        'commons': ['general', 'random'],
        'all_1': '*',
        'all_2': ['*'],
        'empty': [],
    }
    bot = FakeBot(fx_config)
    bot.add_channel('C1', 'general')
    bot.add_channel('C2', 'random')
    bot.add_channel('C3', 'food')
    bot.add_dm('D1', 'U1')
    bot.add_private_channel('G1', 'secret')

    c = ChannelsFromConfig('commons')
    assert c.key == 'commons'

    c_get = c.get()
    assert c_get[0].name == 'general'
    assert c_get[0].id == 'C1'
    assert c_get[1].name == 'random'
    assert c_get[1].id == 'C2'

    with pytest.raises(KeyError):
        ChannelsFromConfig('no').get()

    with pytest.raises(AllChannelsError):
        ChannelsFromConfig('all_1').get()

    with pytest.raises(AllChannelsError):
        ChannelsFromConfig('all_2').get()

    with pytest.raises(NoChannelsError):
        ChannelsFromConfig('empty').get()
