from decimal import Decimal

import pytest

from yui.type import choice, decimal_range, float_range, int_range


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
