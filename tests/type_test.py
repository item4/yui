from decimal import Decimal

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
    Namespace,
    cast,
    choice,
    decimal_range,
    float_range,
    int_range,
)


class User(Namespace):

    id: str
    pw: str
    addresses: Optional[List[str]]


def test_cast():

    ID = NewType('ID', str)

    assert cast(int, '3') == 3
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
    user = cast(User, {'id': 'item4', 'pw': 'supersecret'})
    assert user.id == 'item4'
    assert user.pw == 'supersecret'
    assert user.addresses is None
    users = cast(
        List[User],
        [
            {'id': 'item4', 'pw': 'supersecret'},
            {'id': 'item2', 'pw': 'weak', 'addresses': [1, 2]},
        ]
    )
    assert users[0].id == 'item4'
    assert users[0].pw == 'supersecret'
    assert users[0].addresses is None
    assert users[1].id == 'item2'
    assert users[1].pw == 'weak'
    assert users[1].addresses == ['1', '2']


@pytest.mark.parametrize('cases', [
    ['Dog', 'cat', 'fish'],
    ('Dog', 'cat', 'fish'),
])
def test_choice(cases):

    assert choice(cases)('cat') == 'cat'

    with pytest.raises(ValueError):
        choice(cases)('bird')

    assert choice(cases, fallback='fish')('cat') == 'cat'
    assert choice(cases, fallback='fish')('bird') == 'fish'

    assert choice(cases, case_insensitive=True)('cat') == 'cat'
    assert choice(cases, case_insensitive=True)('dog') == 'dog'
    assert choice(cases, case_insensitive=True)('Dog') == 'Dog'
    assert choice(cases, case_insensitive=True)('DOG') == 'DOG'

    with pytest.raises(ValueError):
        choice(cases, case_insensitive=True)('bird')

    assert choice(cases, fallback='fish', case_insensitive=True)('cat') == \
        'cat'
    assert choice(cases, fallback='fish', case_insensitive=True)('bird') == \
        'fish'
    assert choice(cases, fallback='fish', case_insensitive=True)('dog') == \
        'dog'
    assert choice(cases, fallback='fish', case_insensitive=True)('Dog') == \
        'Dog'
    assert choice(cases, fallback='fish', case_insensitive=True)('DOG') == \
        'DOG'


def test_decimal_range():

    one = Decimal('1')
    five = Decimal('5')

    assert decimal_range(one, five)('3.0') == Decimal('3.0')
    assert decimal_range(one, five, autofix=True)('3.0') == Decimal('3.0')

    with pytest.raises(ValueError):
        decimal_range(one, five)('0.0')

    with pytest.raises(ValueError):
        decimal_range(one, five)('6.0')

    assert decimal_range(one, five, autofix=True)('0.0') == one
    assert decimal_range(one, five, autofix=True)('6.0') == five


def test_float_range():

    assert float_range(1.0, 5.0)('3.0') == 3.0
    assert float_range(1.0, 5.0, autofix=True)('3.0') == 3.0

    with pytest.raises(ValueError):
        float_range(1.0, 5.0)('0.0')

    with pytest.raises(ValueError):
        float_range(1.0, 5.0)('6.0')

    assert float_range(1.0, 5.0, autofix=True)('0.0') == 1.0
    assert float_range(1.0, 5.0, autofix=True)('6.0') == 5.0


def test_int_range():

    assert int_range(1, 5)('3') == 3
    assert int_range(1, 5, autofix=True)('3') == 3

    with pytest.raises(ValueError):
        int_range(1, 5)('0')

    with pytest.raises(ValueError):
        int_range(1, 5)('6')

    assert int_range(1, 5, autofix=True)('0') == 1
    assert int_range(1, 5, autofix=True)('6') == 5
