from decimal import Decimal

import pytest

from yui.type import decimal_range, float_range, int_range


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
