from typing import (
    Any,
    Dict,
    List,
    Mapping,
    MutableSequence,
    NewType,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)

import pytest

from yui.type import (
    AllChannelsError,
    ChannelFromConfig,
    ChannelsFromConfig,
    DirectMessageChannel,
    FromChannelID,
    FromUserID,
    Namespace,
    NoChannelsError,
    PrivateChannel,
    PublicChannel,
    UnknownChannel,
    UnknownUser,
    User,
    cast,
    is_container,
)

from .util import FakeBot


class UserRecord(Namespace):

    id: str
    pw: str
    addresses: Optional[List[str]]


def test_cast():
    bot = FakeBot()
    bot.add_channel('C1', 'general')
    bot.add_channel('C2', 'random')
    bot.add_channel('C3', 'food')
    bot.add_dm('D1', 'U1')
    bot.add_private_channel('G1', 'secret')

    ID = NewType('ID', str)

    assert cast(int, '3') == 3
    assert cast(List[str], ('kirito', 'asuna')) == ['kirito', 'asuna']
    assert cast(List[int], ('1', '2', '3')) == [1, 2, 3]
    assert cast(Sequence[int], ('1', '2', '3')) == [1, 2, 3]
    assert cast(MutableSequence[int], ('1', '2', '3')) == [1, 2, 3]
    assert cast(Tuple[int, float, str], ['1', '2', '3']) == (1, 2.0, '3')
    assert cast(Set[int], ['1', '1', '2']) == {1, 2}
    assert cast(Optional[int], 3) == 3
    assert cast(Optional[int], None) is None
    assert cast(Union[int, float], '3.2') == 3.2
    assert cast(List[ID], [1, 2, 3]) == [ID(1), ID(2), ID(3)]
    assert cast(Dict[str, Any], {1: 1, 2: 2.2}) == {'1': 1, '2': 2.2}
    assert cast(Mapping[str, str], {1: 1, 2: 2.2}) == {'1': '1', '2': '2.2'}
    assert cast(List, ('kirito', 'asuna', 16.5)) == ['kirito', 'asuna', 16.5]
    assert cast(Sequence, ('kirito', 'asuna', 16.5)) == [
        'kirito', 'asuna', 16.5]
    assert cast(MutableSequence, ('kirito', 'asuna', 16.5)) == [
        'kirito', 'asuna', 16.5]
    assert cast(Tuple, ['1', 2, 3.0]) == ('1', 2, 3.0)
    assert cast(Set, {'1', 2, 3.0, 2}) == {'1', 2, 3.0}
    assert cast(Dict, {'1': 'kirito', 2: 'asuna', 3: 16.5}) == {
        '1': 'kirito',
        2: 'asuna',
        3: 16.5,
    }
    assert cast(Mapping, {'1': 'kirito', 2: 'asuna', 3: 16.5}) == {
        '1': 'kirito',
        2: 'asuna',
        3: 16.5,
    }
    user = cast(UserRecord, {'id': 'item4', 'pw': 'supersecret'})
    assert user.id == 'item4'
    assert user.pw == 'supersecret'
    assert not hasattr(user, 'addresses')
    users = cast(
        List[UserRecord],
        [
            {'id': 'item4', 'pw': 'supersecret'},
            {'id': 'item2', 'pw': 'weak', 'addresses': [1, 2]},
        ]
    )
    assert users[0].id == 'item4'
    assert users[0].pw == 'supersecret'
    assert not hasattr(users[0], 'addresses')
    assert users[1].id == 'item2'
    assert users[1].pw == 'weak'
    assert users[1].addresses == ['1', '2']

    with pytest.raises(ValueError):
        cast(Union[int, float], 'asdf')

    channel = cast(FromChannelID, 'C1')
    assert isinstance(channel, PublicChannel)
    assert channel.id == 'C1'
    assert channel.name == 'general'

    dm = cast(FromChannelID, 'D1')
    assert isinstance(dm, DirectMessageChannel)
    assert dm.id == 'D1'
    assert dm.user == 'U1'

    dm = cast(FromChannelID, 'D2')
    assert isinstance(dm, UnknownChannel)
    assert dm.id == 'D2'

    group = cast(FromChannelID, 'G1')
    assert isinstance(group, PrivateChannel)
    assert group.id == 'G1'
    assert group.name == 'secret'

    unknown = cast(FromChannelID, 'G2')
    assert isinstance(unknown, UnknownChannel)
    assert unknown.id == 'G2'

    unexpected = cast(FromChannelID, {'id': 'C5', 'name': 'firefox'})
    assert isinstance(unexpected, FromChannelID)
    assert unexpected.id == 'C5'
    assert unexpected.name == 'firefox'


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


def test_is_container():
    assert is_container(List[int])
    assert is_container(Set[int])
    assert is_container(Tuple[int])
    assert is_container(list)
    assert is_container(set)
    assert is_container(tuple)
    assert not is_container(int)
    assert not is_container(float)
    assert not is_container(bool)


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
