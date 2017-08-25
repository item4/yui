from decimal import Decimal

import pytest

from yui.type import DecimalRange, FloatRange, IntRange, Range


def test_range():

    assert Range[int](int, 1, 5)('3') == 3
    assert Range[int](int, 1, 5, autofix=True)('3') == 3

    with pytest.raises(ValueError):
        Range[int](int, 1, 5)('0')

    with pytest.raises(ValueError):
        Range[int](int, 1, 5)('6')

    assert Range[int](int, 1, 5, autofix=True)('0') == 1
    assert Range[int](int, 1, 5, autofix=True)('6') == 5


def test_decimal_range():

    one = Decimal('1')
    five = Decimal('5')

    assert DecimalRange(one, five)('3.0') == Decimal('3.0')
    assert DecimalRange(one, five, autofix=True)('3.0') == Decimal('3.0')

    with pytest.raises(ValueError):
        DecimalRange(one, five)('0.0')

    with pytest.raises(ValueError):
        DecimalRange(one, five)('6.0')

    assert DecimalRange(one, five, autofix=True)('0.0') == one
    assert DecimalRange(one, five, autofix=True)('6.0') == five


def test_float_range():

    assert FloatRange(1.0, 5.0)('3.0') == 3.0
    assert FloatRange(1.0, 5.0, autofix=True)('3.0') == 3.0

    with pytest.raises(ValueError):
        FloatRange(1.0, 5.0)('0.0')

    with pytest.raises(ValueError):
        FloatRange(1.0, 5.0)('6.0')

    assert FloatRange(1.0, 5.0, autofix=True)('0.0') == 1.0
    assert FloatRange(1.0, 5.0, autofix=True)('6.0') == 5.0


def test_int_range():

    assert IntRange(1, 5)('3') == 3
    assert IntRange(1, 5, autofix=True)('3') == 3

    with pytest.raises(ValueError):
        IntRange(1, 5)('0')

    with pytest.raises(ValueError):
        IntRange(1, 5)('6')

    assert IntRange(1, 5, autofix=True)('0') == 1
    assert IntRange(1, 5, autofix=True)('6') == 5
