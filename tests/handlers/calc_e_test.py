import pytest

from yui.handlers.calc import Evaluator


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
