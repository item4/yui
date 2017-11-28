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
    DirectMessageChannel,
    FromChannelID,
    Namespace,
    PrivateChannel,
    PublicChannel,
    cast,
    is_container,
)

from .util import FakeBot


class User(Namespace):

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
    user = cast(User, {'id': 'item4', 'pw': 'supersecret'})
    assert user.id == 'item4'
    assert user.pw == 'supersecret'
    assert not hasattr(user, 'addresses')
    users = cast(
        List[User],
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
    assert isinstance(dm, DirectMessageChannel)
    assert dm.id == 'D2'

    group = cast(FromChannelID, 'G1')
    assert isinstance(group, PrivateChannel)
    assert group.id == 'G1'
    assert group.name == 'secret'

    with pytest.raises(KeyError):
        cast(FromChannelID, 'G2')

    unexpected = cast(FromChannelID, {'id': 'C5', 'name': 'firefox'})
    assert isinstance(unexpected, FromChannelID)
    assert unexpected.id == 'C5'
    assert unexpected.name == 'firefox'


def test_from_channel_id():
    bot = FakeBot()
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

    with pytest.raises(KeyError):
        FromChannelID.from_id('G2')

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
