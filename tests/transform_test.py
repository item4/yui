import enum

from decimal import Decimal

import pytest

from yui.transform import choice, enum_getitem, value_range


def test_enum_getitem():
    """Test enum_getitem helper."""

    class A(enum.Enum):
        a = 1
        b = 2
        c = 3

    assert enum_getitem(A)('a') == A.a

    with pytest.raises(ValueError):
        enum_getitem(A)('zzz')

    assert enum_getitem(A, fallback='b')('a') == A.a
    assert enum_getitem(A, fallback='b')('zzz') == A.b


@pytest.mark.parametrize('items', [
    ['Dog', 'cat', 'fish'],
    ('Dog', 'cat', 'fish'),
])
def test_choice(items):

    assert choice(items)('cat') == 'cat'

    with pytest.raises(ValueError):
        choice(items)('bird')

    assert choice(items, fallback='fish')('cat') == 'cat'
    assert choice(items, fallback='fish')('bird') == 'fish'

    assert choice(items, case_insensitive=True)('cat') == 'cat'
    assert choice(items, case_insensitive=True)('dog') == 'dog'
    assert choice(items, case_insensitive=True)('Dog') == 'Dog'
    assert choice(items, case_insensitive=True)('DOG') == 'DOG'

    assert choice(items, case='lower')('cat') == 'cat'
    assert choice(items, case='lower')('Dog') == 'dog'

    with pytest.raises(ValueError):
        choice(items, case='lower')('DOG')

    assert choice(items, case='lower', fallback='fish')('cat') == 'cat'
    assert choice(items, case='lower', fallback='fish')('Dog') == 'dog'
    assert choice(items, case='lower', fallback='fish')('bird') == 'fish'

    assert choice(items, case='lower', case_insensitive=True)('cat') == 'cat'
    assert choice(items, case='lower', case_insensitive=True)('CAT') == 'cat'

    assert choice(items, case_insensitive=True)('cat') == 'cat'

    with pytest.raises(ValueError):
        choice(items, case_insensitive=True)('bird')

    assert choice(items, fallback='fish', case_insensitive=True)('cat') == \
        'cat'
    assert choice(items, fallback='fish', case_insensitive=True)('bird') == \
        'fish'
    assert choice(items, fallback='fish', case_insensitive=True)('dog') == \
        'dog'
    assert choice(items, fallback='fish', case_insensitive=True)('Dog') == \
        'Dog'
    assert choice(items, fallback='fish', case_insensitive=True)('DOG') == \
        'DOG'


def test_value_range():

    # Decimal
    one = Decimal('1')
    three = Decimal('3.0')
    five = Decimal('5')

    assert value_range(one, five)(three) == Decimal(three)
    assert value_range(one, five, autofix=True)(three) == Decimal(three)

    with pytest.raises(ValueError):
        value_range(one, five)(Decimal('0.0'))

    with pytest.raises(ValueError):
        value_range(one, five)(Decimal('6.0'))

    assert value_range(one, five, autofix=True)(Decimal('0.0')) == one
    assert value_range(one, five, autofix=True)(Decimal('6.0')) == five

    # float

    assert value_range(1.0, 5.0)(3.0) == 3.0
    assert value_range(1.0, 5.0, autofix=True)(3.0) == 3.0

    with pytest.raises(ValueError):
        value_range(1.0, 5.0)(0.0)

    with pytest.raises(ValueError):
        value_range(1.0, 5.0)(6.0)

    assert value_range(1.0, 5.0, autofix=True)(0.0) == 1.0
    assert value_range(1.0, 5.0, autofix=True)(6.0) == 5.0

    # int

    assert value_range(1, 5)(3) == 3
    assert value_range(1, 5, autofix=True)(3) == 3

    with pytest.raises(ValueError):
        value_range(1, 5)(0)

    with pytest.raises(ValueError):
        value_range(1, 5)(6)

    assert value_range(1, 5, autofix=True)(0) == 1
    assert value_range(1, 5, autofix=True)(6) == 5
