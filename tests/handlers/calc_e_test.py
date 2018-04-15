import pytest

from yui.handlers.calc import BadSyntax, Evaluator


def test_asyncfunctiondef():
    e = Evaluator()
    err = 'Defining new coroutine via def syntax is not allowed'
    with pytest.raises(BadSyntax, match=err):
        e.run('''
async def abc():
    pass

''')
    assert 'abc' not in e.symbol_table


def test_assign():
    e = Evaluator()
    e.run('a = 1 + 2')
    assert e.symbol_table['a'] == 3
    e.run('x, y = 10, 20')
    assert e.symbol_table['x'] == 10
    assert e.symbol_table['y'] == 20


def test_binop():
    e = Evaluator()
    assert e.run('1 + 2') == 1 + 2
    assert e.run('3 & 2') == 3 & 2
    assert e.run('1 | 2') == 1 | 2
    assert e.run('3 ^ 2') == 3 ^ 2
    assert e.run('3 / 2') == 3 / 2
    assert e.run('3 // 2') == 3 // 2
    assert e.run('3 << 2') == 3 << 2
    with pytest.raises(TypeError):
        e.run('2 @ 3')
    assert e.run('3 * 2') == 3 * 2
    assert e.run('33 % 4') == 33 % 4
    assert e.run('3 ** 2') == 3 ** 2
    assert e.run('100 >> 2') == 100 >> 2
    assert e.run('3 - 1') == 3 - 1


def test_boolop():
    e = Evaluator()
    assert e.run('True and False') == (True and False)
    assert e.run('True or False') == (True or False)


def test_bytes():
    e = Evaluator()
    assert e.run('b"asdf"') == b'asdf'
    e.run('a = b"asdf"')
    assert e.symbol_table['a'] == b'asdf'


def test_classdef():
    e = Evaluator()
    err = 'Defining new class via def syntax is not allowed'
    with pytest.raises(BadSyntax, match=err):
        e.run('''
class ABCD:
    pass

''')
    assert 'ABCD' not in e.symbol_table


def test_compare():
    e = Evaluator()
    assert e.run('1 == 2') == (1 == 2)
    assert e.run('3 > 2') == (3 > 2)
    assert e.run('3 >= 2') == (3 >= 2)
    assert e.run('"A" in "America"') == ('A' in 'America')
    assert e.run('"E" not in "America"') == ('E' not in 'America')
    assert e.run('1 is 2') == (1 is 2)
    assert e.run('1 is not 2') == (1 is not 2)
    assert e.run('3 < 2') == (3 < 2)
    assert e.run('3 <= 2') == (3 <= 2)


def test_dict():
    e = Evaluator()
    assert e.run('{1: 111, 2: 222}') == {1: 111, 2: 222}
    e.run('a = {1: 111, 2: 222}')
    assert e.symbol_table['a'] == {1: 111, 2: 222}


def test_ellipsis():
    e = Evaluator()
    assert e.run('...') == Ellipsis


def test_expr():
    e = Evaluator()
    assert e.run('True') is True
    assert e.run('False') is False
    assert e.run('None') is None
    assert e.run('123') == 123
    assert e.run('"abc"') == 'abc'
    assert e.run('[1, 2, 3]') == [1, 2, 3]
    assert e.run('(1, 2, 3, 3)') == (1, 2, 3, 3)
    assert e.run('{1, 2, 3, 3}') == {1, 2, 3}
    assert e.run('{1: 111, 2: 222}') == {1: 111, 2: 222}


def test_functiondef():
    e = Evaluator()
    err = 'Defining new function via def syntax is not allowed'
    with pytest.raises(BadSyntax, match=err):
        e.run('''
def abc():
    pass

''')
    assert 'abc' not in e.symbol_table


def test_if():
    e = Evaluator()
    e.symbol_table['a'] = 1
    e.run('''
if a == 1:
    a = 2
    b = 3
''')
    assert e.symbol_table['a'] == 2
    assert e.symbol_table['b'] == 3

    e.run('''
if a == 1:
    a = 2
    b = 3
    z = 1
else:
    a = 3
    b = 4
    c = 5
''')
    assert e.symbol_table['a'] == 3
    assert e.symbol_table['b'] == 4
    assert e.symbol_table['c'] == 5
    assert 'z' not in e.symbol_table

    e.run('''
if a == 1:
    a = 2
    b = 3
    z = 1
elif a == 3:
    d = 4
    e = 5
    f = 6
else:
    a = 3
    b = 4
    c = 5
    y = 7
''')
    assert e.symbol_table['a'] == 3
    assert e.symbol_table['b'] == 4
    assert e.symbol_table['c'] == 5
    assert e.symbol_table['d'] == 4
    assert e.symbol_table['e'] == 5
    assert e.symbol_table['f'] == 6
    assert 'y' not in e.symbol_table
    assert 'z' not in e.symbol_table


def test_ifexp():
    e = Evaluator()
    assert e.run('100 if 1 == 1 else 200') == 100
    assert e.run('100 if 1 == 2 else 200') == 200


def test_import():
    e = Evaluator()
    err = 'You can not import anything'
    with pytest.raises(BadSyntax, match=err):
        e.run('import sys')
    assert 'sys' not in e.symbol_table


def test_importfrom():
    e = Evaluator()
    err = 'You can not import anything'
    with pytest.raises(BadSyntax, match=err):
        e.run('from os import path')
    assert 'path' not in e.symbol_table


def test_lambda():
    e = Evaluator()
    err = 'Defining new function via lambda syntax is not allowed'
    with pytest.raises(BadSyntax, match=err):
        e.run('lambda x: x*2')


def test_list():
    e = Evaluator()
    assert e.run('[1, 2, 3]') == [1, 2, 3]
    e.run('a = [1, 2, 3]')
    assert e.symbol_table['a'] == [1, 2, 3]


def test_listcomp():
    e = Evaluator()
    assert e.run('[x ** 2 for x in [1, 2, 3]]') == [1, 4, 9]
    assert 'x' not in e.symbol_table
    assert e.run('[x ** 2 + y for x in [1, 2, 3] for y in [10, 20, 30]]') == (
        [x ** 2 + y for x in [1, 2, 3] for y in [10, 20, 30]]
    )
    assert 'x' not in e.symbol_table
    assert 'y' not in e.symbol_table
    assert e.run('[y ** 2 for x in [1, 2, 3] for y in [x+1, x+3, x+5]]') == (
        [y ** 2 for x in [1, 2, 3] for y in [x+1, x+3, x+5]]
    )
    assert 'x' not in e.symbol_table
    assert 'y' not in e.symbol_table


def test_nameconstant():
    e = Evaluator()
    assert e.run('True') is True
    assert e.run('False') is False
    assert e.run('None') is None
    e.run('x = True')
    e.run('y = False')
    e.run('z = None')
    assert e.symbol_table['x'] is True
    assert e.symbol_table['y'] is False
    assert e.symbol_table['z'] is None


def test_num():
    e = Evaluator()
    assert e.run('123') == 123
    e.run('a = 123')
    assert e.symbol_table['a'] == 123


def test_set():
    e = Evaluator()
    assert e.run('{1, 1, 2, 3, 3}') == {1, 2, 3}
    e.run('a = {1, 1, 2, 3, 3}')
    assert e.symbol_table['a'] == {1, 2, 3}


def test_setcomp():
    e = Evaluator()
    assert e.run('{x ** 2 for x in [1, 2, 3, 3]}') == {1, 4, 9}
    assert 'x' not in e.symbol_table
    assert e.run('{x ** 2 + y for x in [1, 2, 3] for y in [10, 20, 30]}') == (
        {x ** 2 + y for x in [1, 2, 3] for y in [10, 20, 30]}
    )
    assert 'x' not in e.symbol_table
    assert 'y' not in e.symbol_table
    assert e.run('{y ** 2 for x in [1, 2, 3] for y in [x+1, x+3, x+5]}') == (
        {y ** 2 for x in [1, 2, 3] for y in [x+1, x+3, x+5]}
    )
    assert 'x' not in e.symbol_table
    assert 'y' not in e.symbol_table


def test_str():
    e = Evaluator()
    assert e.run('"asdf"') == 'asdf'
    e.run('a = "asdf"')
    assert e.symbol_table['a'] == 'asdf'


def test_tuple():
    e = Evaluator()
    assert e.run('(1, 1, 2, 3, 3)') == (1, 1, 2, 3, 3)
    e.run('a = (1, 1, 2, 3, 3)')
    assert e.symbol_table['a'] == (1, 1, 2, 3, 3)


def test_unaryop():
    e = Evaluator()
    assert e.run('~100') == ~100
    assert e.run('not 100') == (not 100)
    assert e.run('+100') == +100
    assert e.run('-100') == -100
