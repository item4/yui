from typing import Any, Dict, List, NewType, Optional, Set, Tuple, Union

import pytest

from yui.types.namespace import Field, namespace
from yui.utils.cast import cast

from ..util import FakeBot


@namespace
class UserRecord:

    id: str
    pw: str
    addresses: List[str] = Field(
        converter=lambda v: None if v is None else [str(i) for i in v],
    )


def test_cast():
    bot = FakeBot()
    bot.add_user('U1', 'kirito')
    bot.add_channel('C1', 'general')
    bot.add_channel('C2', 'random')
    bot.add_channel('C3', 'food')
    bot.add_dm('D1', 'U1')
    bot.add_private_channel('G1', 'secret')

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
    assert user.addresses is None
    users = cast(
        List[UserRecord],
        [
            {'id': 'item4', 'pw': 'supersecret'},
            {'id': 'item2', 'pw': 'weak', 'addresses': [1, 2]},
        ],
    )
    assert users[0].id == 'item4'
    assert users[0].pw == 'supersecret'
    assert users[0].addresses is None
    assert users[1].id == 'item2'
    assert users[1].pw == 'weak'
    assert users[1].addresses == ['1', '2']

    with pytest.raises(ValueError):
        cast(Union[int, float], 'asdf')
