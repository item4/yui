import math

import pytest

from yui.handlers.calc import Decimal as D, calculate


@pytest.mark.parametrize(
    ('expr, expected_decimal_result, expected_num_result,'
     'expected_decimal_local, expected_num_local'),
    [
        ('1', D('1'), 1, {}, {}),
        ('1+2', D('3'), 3, {}, {}),
        (
            '0.1+0.1+0.1+0.1+0.1+0.1+0.1+0.1+0.1+0.1',
            D('1'),
            0.1+0.1+0.1+0.1+0.1+0.1+0.1+0.1+0.1+0.1,
            {},
            {}
        ),
        ('1-2', D('-1'), -1, {}, {}),
        ('4*5', D('20'), 20, {}, {}),
        ('1/2', D('0.5'), 0.5, {}, {}),
        ('10%3', D('1'), 1, {}, {}),
        ('2**3', D('8'), 8, {}, {}),
        ('(1+2)**3', D('27'), 27, {}, {}),
        ('max(1,2,3,4,5)', D('5'), 5, {}, {}),
        ('floor(3.2)', D('3'), 3, {}, {}),
        ('round', round, round, {}, {}),
        ('math', math, math, {}, {}),
        ('1+e', D(math.e) + D('1'), math.e + 1, {}, {}),
        ('[1,2,3]', [D('1'), D('2'), D('3')], [1, 2, 3], {}, {}),
        (
            '[x*10 for x in [0,1,2]]',
            [D('0'), D('10'), D('20')],
            [0, 10, 20],
            {},
            {}
        ),
        ('(1,2,3)', (D('1'), D('2'), D('3')), (1, 2, 3), {}, {}),
        ('{3,2,10}', {D('2'), D('3'), D('10')}, {2, 3, 10}, {}, {}),
        ('{x%2 for x in [1,2,3,4]}', {D('0'), D('1')}, {0, 1}, {}, {}),
        ('{"ab": 123}', {'ab': D('123')}, {'ab': 123}, {}, {}),
        (
            '{"k"+str(x): x-1 for x in [1,2,3]}',
            {'k1': D('0'), 'k2': D('1'), 'k3': D('2')},
            {'k1': 0, 'k2': 1, 'k3': 2},
            {},
            {}
        ),
        ('3 in [1,2,3]', True, True, {}, {}),
        ('[1,2,3,12,3].count(3)', 2, 2, {}, {}),
        ('{1,2} & {2,3}', {D('2')}, {2}, {}, {}),
        ('"item4"', 'item4', 'item4', {}, {}),
        ('"{}4".format("item")', 'item4', 'item4', {}, {}),
        ('money = 1000', None, None, {'money': D('1000')}, {'money': 1000}),
        (
            'money = 1000; money * 2',
            D('2000'),
            2000,
            {'money': D('1000')},
            {'money': 1000}
        ),
        (
            'money = 1000; f"{money}원"',
            '1000원',
            '1000원',
            {'money': D('1000')},
            {'money': 1000}
        ),
        (
            'f = lambda x: x*2; f(10)',
            D('20'),
            20,
            {'f': lambda x: x*D(2)},
            {'f': lambda x: x*2}
        ),
    ]
)
def test_calculate_fine(
    expr: str,
    expected_decimal_result,
    expected_num_result,
    expected_decimal_local: dict,
    expected_num_local: dict,
):

    decimal_result, decimal_local = calculate(
        expr, replace_num_to_decimal=True)

    num_result, num_local = calculate(expr, replace_num_to_decimal=False)

    assert expected_decimal_result == decimal_result
    assert expected_decimal_local.keys() == decimal_local.keys()

    for key in decimal_local.keys():
        e = expected_decimal_local[key]
        l = decimal_local[key]

        assert type(e) == type(l)

        if callable(e):
            assert e(1) == l(1)
        else:
            assert e == l

    assert expected_num_result == num_result
    assert expected_num_local.keys() == num_local.keys()

    for key in num_local.keys():
        e = expected_num_local[key]
        l = num_local[key]

        assert type(e) == type(l)

        if callable(e):
            assert e(1) == l(1)
        else:
            assert e == l


def test_calculate_magic():
    """calculate will make result as list what typed such as
    range, map, filter, enumerate, zip automatically."""

    result, local = calculate('range(4)', replace_num_to_decimal=False)
    assert result == [0, 1, 2, 3]
    assert not local

    result, local = calculate(
        'filter(lambda x: x&1, range(4))',
        replace_num_to_decimal=False
    )
    assert result == [1, 3]
    assert not local

    result, local = calculate(
        'map(lambda x: x*100, range(4))',
        replace_num_to_decimal=False
    )
    assert result == [0, 100, 200, 300]
    assert not local

    result, local = calculate(
        'enumerate(["i", "t", "e", "m"])',
        replace_num_to_decimal=False
    )
    assert result == [(0, 'i'), (1, 't'), (2, 'e'), (3, 'm')]
    assert not local

    result, local = calculate(
        'zip(["i", "t", "e", "m"], [10, 21, 32, 43])',
        replace_num_to_decimal=False
    )
    assert result == [('i', 10), ('t', 21), ('e', 32), ('m', 43)]
    assert not local


@pytest.mark.parametrize(
    'expr, error, message',
    [
        ('+', SyntaxError, 'invalid syntax'),
        ('def a(): pass', SyntaxError, 'func def is not permitted.'),
        ('async def a(): pass', SyntaxError,
         'async func def is not permitted.'),
        ('class A: pass', SyntaxError, 'class def is not permitted.'),
        ('return', SyntaxError, 'return is not permitted.'),
        ('for x in arr: pass', SyntaxError, 'for stmt is not permitted.'),
        ('while True: pass', SyntaxError, 'while stmt is not permitted.'),
        ('if True: pass', SyntaxError, 'if stmt is not permitted.'),
        ('if True:\n  pass\nelse:\n  pass\n', SyntaxError,
         'if stmt is not permitted.'),
        ('with a: pass', SyntaxError, 'with stmt is not permitted.'),
        ('raise SystemExit()', SyntaxError, 'raise stmt is not permitted.'),
        ('try:\n  pass\nexcept:\n  pass\n', SyntaxError,
         'try stmt is not permitted.'),
        ('assert True', SyntaxError, 'assert stmt is not permitted.'),
        ('import sys', SyntaxError, 'import is not permitted.'),
        ('from os import path', SyntaxError, 'import is not permitted.'),
        ('global a', SyntaxError, 'global stmt is not permitted.'),
        ('nonlocal a', SyntaxError, 'nonlocal stmt is not permitted.'),
        ('pass', SyntaxError, 'pass stmt is not permitted.'),
        ('break', SyntaxError, 'break stmt is not permitted.'),
        ('continue', SyntaxError, 'continue stmt is not permitted.'),
        ('a()', SyntaxError, 'call a is not permitted.'),
        ('dict = 1', SyntaxError, 'override builtins is not permitted.'),
        ('a.a()', SyntaxError, 'call a.a is not permitted.'),
        ('floor.__func__', SyntaxError,
         'access to floor.__func__ attr is not permitted.'),
        ('(1).__class__', SyntaxError,
         'access to Decimal\\(\\).__class__ attr is not permitted.'),
    ]
)
def test_calculate_error(expr: str, error, message: str):

    with pytest.raises(error, match=message):
        calculate(expr)
