from typing import Any, Dict, List, NewType, Optional, Set, Tuple, Union

import pytest

from yui.types.namespace.base import Namespace
from yui.types.namespace.linked import (
    DirectMessageChannel,
    FromChannelID,
    FromUserID,
    PrivateChannel,
    PublicChannel,
    UnknownChannel,
    UnknownUser,
    User,
)
from yui.utils.cast import cast

from ..util import FakeBot


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
    bot.add_user('U1', 'kirito')

    ID = NewType('ID', str)

    assert cast(int, '3') == 3
    assert cast(List[str], ('kirito', 'asuna')) == ['kirito', 'asuna']
    assert cast(List[int], ('1', '2', '3')) == [1, 2, 3]
    assert cast(Tuple[int, float, str], ['1', '2', '3']) == (1, 2.0, '3')
    assert cast(Set[int], ['1', '1', '2']) == {1, 2}
    assert cast(Optional[int], 3) == 3
    assert cast(Optional[int], None) is None
    assert cast(Union[int, float], '3.2') == 3.2
    assert cast(List[ID], [1, 2, 3]) == [ID('1'), ID('2'), ID('3')]
    assert cast(Dict[str, Any], {1: 1, 2: 2.2}) == {'1': 1, '2': 2.2}
    assert cast(Dict[str, str], {1: 1, 2: 2.2}) == {'1': '1', '2': '2.2'}
    assert cast(List, ('kirito', 'asuna', 16.5)) == ['kirito', 'asuna', 16.5]
    assert cast(Tuple, ['1', 2, 3.0]) == ('1', 2, 3.0)
    assert cast(Set, {'1', 2, 3.0, 2}) == {'1', 2, 3.0}
    assert cast(Dict, {'1': 'kirito', 2: 'asuna', 3: 16.5}) == {
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

    kirito = cast(FromUserID, 'U1')
    assert isinstance(kirito, User)
    assert kirito.id == 'U1'
    assert kirito.name == 'kirito'

    poh = cast(FromUserID, 'UPOH')
    assert isinstance(poh, UnknownUser)
    assert poh.id == 'UPOH'

    unexpected = cast(FromUserID, {'id': 'U4', 'name': 'chrome'})
    assert isinstance(unexpected, FromUserID)
    assert unexpected.id == 'U4'
    assert unexpected.name == 'chrome'
