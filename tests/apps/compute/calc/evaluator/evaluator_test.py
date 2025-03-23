import functools
import html
import math
from datetime import date

import pytest

from yui.apps.compute.calc.evaluator import Evaluator
from yui.apps.compute.calc.evaluator import ScopeStack
from yui.apps.compute.calc.exceptions import BadSyntax
from yui.apps.compute.calc.exceptions import CallableKeywordsError
from yui.apps.compute.calc.exceptions import NotCallableError
from yui.apps.compute.calc.exceptions import NotIterableError
from yui.apps.compute.calc.exceptions import NotSubscriptableError
from yui.apps.compute.calc.types import Decimal as D
from yui.utils import datetime


class GetItemSpy:
    def __init__(self):
        self.queue = []

    def __getitem__(self, item):
        self.queue.append(item)


def test_scope_stack():
    scope = ScopeStack()

    with pytest.raises(NameError):
        _ = scope["undefined"]

    with pytest.raises(NameError):
        del scope["undefined"]


def test_assign(e):
    e.run("a = 1 + 2")
    assert e.scope["a"] == 3
    e.run("x, y = 10, 20")
    assert e.scope["x"] == 10
    assert e.scope["y"] == 20

    e.scope["dt"] = datetime.now()
    err = "This assign method is not allowed"
    with pytest.raises(BadSyntax, match=err):
        e.run("dt.year = 2000")

    err = "too many values to unpack"
    with pytest.raises(ValueError, match=err):
        e.run("year, month, day = 1,")

    err = "not enough values to unpack"
    with pytest.raises(ValueError, match=err):
        e.run('id, name = 1, "kirito", "black"')

    err = "'int' object is not iterable"
    with pytest.raises(NotIterableError, match=err):
        e.run("year, month, day = 1")

    e.run("arr = [1, 2, 3]")
    assert e.scope["arr"] == [1, 2, 3]

    e.run("arr[1] = 5")
    assert e.scope["arr"] == [1, 5, 3]

    e.run("arr[:] = [10, 20, 30]")
    assert e.scope["arr"] == [10, 20, 30]

    e.scope["text"] = "kirito"
    err = "'str' object is not subscriptable"
    with pytest.raises(NotSubscriptableError, match=err):
        e.run("text[3] = 'x'")


def test_attribute(e):
    e.scope["dt"] = datetime.now()
    e.run("x = dt.year")
    assert e.scope["x"] == e.scope["dt"].year

    err = "You can not access `test_test_test` attribute"
    with pytest.raises(BadSyntax, match=err):
        e.run("y = dt.test_test_test")

    assert "y" not in e.scope

    err = "You can not access `asdf` attribute"
    with pytest.raises(BadSyntax, match=err):
        e.run("z = x.asdf")

    e.scope["math"] = math
    err = "You can not access `__module__` attribute"
    with pytest.raises(BadSyntax, match=err):
        e.run("math.__module__")

    e.scope["functools"] = functools
    err = "You can not access `test_test` attribute"
    with pytest.raises(BadSyntax, match=err):
        e.run("functools.test_test")

    err = "You can not access attributes of "
    with pytest.raises(BadSyntax, match=err):
        e.run("Decimal.test_test")


def test_augassign(e):
    e.scope["a"] = 0
    e.run("a += 1")
    assert e.scope["a"] == 1
    e.scope["l"] = [1, 2, 3, 4]
    e.run("l[0] -= 1")
    assert e.scope["l"] == [0, 2, 3, 4]

    err = "This assign method is not allowed"
    with pytest.raises(BadSyntax, match=err):
        e.run("l[2:3] += 20")

    e.scope["dt"] = datetime.now()
    err = "This assign method is not allowed"
    with pytest.raises(BadSyntax, match=err):
        e.run("dt.year += 2000")

    e.scope["text"] = "kirito"
    err = "'str' object is not subscriptable"
    with pytest.raises(NotSubscriptableError, match=err):
        e.run("text[3] += 'x'")


def test_bytes(e):
    assert e.run('b"asdf"') == b"asdf"
    e.run('a = b"asdf"')
    assert e.scope["a"] == b"asdf"


def test_call(e):
    e.scope["date"] = date
    e.run("x = date(2019, 10, day=7)")
    assert e.scope["x"] == date(2019, 10, day=7)

    e.scope["math"] = math
    e.run("y = math.sqrt(121)")
    assert e.scope["y"] == math.sqrt(121)

    e.run("z = html.escape('<hello>')")
    assert e.scope["z"] == html.escape("<hello>")

    e.scope["kwd"] = {0: 2020, 1: 3, 2: 10}
    err = "keywords must be strings"
    with pytest.raises(CallableKeywordsError, match=err):
        e.run("date(**kwd)")

    err = "'float' object is not callable"
    with pytest.raises(NotCallableError, match=err):
        e.run("pi()")


def test_compare(e):
    assert e.run("1 == 2") is (1 == 2)  # noqa: PLR0133
    assert e.run("3 > 2") is (3 > 2)  # noqa: PLR0133
    assert e.run("3 >= 2") is (3 >= 2)  # noqa: PLR0133
    assert e.run('"A" in "America"') is ("A" in "America")  # noqa: PLR0133
    assert e.run('"E" not in "America"') is (
        "E" not in "America"  # noqa: PLR0133
    )
    assert e.run("1 is 2") is (1 is 2)  # noqa: F632 PLR0133
    assert e.run("1 is not 2") is (1 is not 2)  # noqa: F632 PLR0133
    assert e.run("3 < 2") is (3 < 2)  # noqa: PLR0133
    assert e.run("3 <= 2") is (3 <= 2)  # noqa: PLR0133


def test_constant():
    e1 = Evaluator()
    e2 = Evaluator(decimal_mode=True)
    assert e1.run("1.2") == 1.2
    assert e2.run("1.2") == D("1.2")
    assert e1.run("...") == Ellipsis
    assert e2.run("...") == Ellipsis


def test_delete(e):
    e.scope["a"] = 0
    e.scope["b"] = 0
    e.scope["c"] = 0
    e.scope["d"] = 0
    e.run("del a, b, c")
    assert "a" not in e.scope
    assert "b" not in e.scope
    assert "c" not in e.scope
    assert "d" in e.scope
    e.run("del d")
    assert "d" not in e.scope
    e.scope["l"] = [1, 2, 3, 4]
    e.run("del l[0]")
    assert e.scope["l"] == [2, 3, 4]

    err = "This delete method is not allowed"
    with pytest.raises(BadSyntax, match=err):
        e.run("del l[2:3]")

    e.scope["dt"] = datetime.now()
    err = "This delete method is not allowed"
    with pytest.raises(BadSyntax, match=err):
        e.run("del dt.year")

    e.scope["text"] = "kirito"
    err = "'str' object is not subscriptable"
    with pytest.raises(NotSubscriptableError, match=err):
        e.run("del text[3]")


def test_dict(e):
    assert e.run("{1: 111, 2: 222}") == {1: 111, 2: 222}
    e.run("a = {1: 111, 2: 222}")
    assert e.scope["a"] == {1: 111, 2: 222}


def test_expr(e):
    assert e.run("True") is True
    assert e.run("False") is False
    assert e.run("None") is None
    assert e.run("123") == 123
    assert e.run('"abc"') == "abc"
    assert e.run("[1, 2, 3]") == [1, 2, 3]
    assert e.run("(1, 2, 3, 3)") == (1, 2, 3, 3)
    assert e.run("{1, 2, 3, 3}") == {1, 2, 3}
    assert e.run("{1: 111, 2: 222}") == {1: 111, 2: 222}
    with pytest.raises(NameError):
        e.run("undefined_variable")


def test_formattedvalue(e):
    e.scope["before"] = 123456
    e.run('after = f"change {before} to {before:,}!"')
    assert e.scope["after"] == "change 123456 to 123,456!"


def test_if_simple(e):
    e.scope["x"] = 1
    e.run(
        """\
if x == 1:
    a = 2
    b = 3
""",
    )
    assert e.scope["a"] == 2
    assert e.scope["b"] == 3


def test_if_else(e):
    e.scope["x"] = 10
    e.run(
        """\
if x == 1:
    a = 2
    b = 3
    z = 1
else:
    a = 3
    b = 4
    c = 5
""",
    )
    assert e.scope["a"] == 3
    assert e.scope["b"] == 4
    assert e.scope["c"] == 5
    assert "z" not in e.scope


def test_if_elif(e):
    e.scope["x"] = 3
    e.run(
        """\
if x == 1:
    a = 2
    b = 3
    c = 1
elif x == 3:
    d = 4
    e = 5
    f = 6
""",
    )
    assert "a" not in e.scope
    assert "b" not in e.scope
    assert "c" not in e.scope
    assert e.scope["d"] == 4
    assert e.scope["e"] == 5
    assert e.scope["f"] == 6


def test_if_elif_else(e):
    e.scope["x"] = 3
    e.run(
        """\
if x == 1:
    a = 2
    b = 3
    z = 1
elif x == 3:
    d = 4
    e = 5
    f = 6
else:
    a = 3
    b = 4
    c = 5
    y = 7
""",
    )
    assert "a" not in e.scope
    assert "b" not in e.scope
    assert "z" not in e.scope
    assert e.scope["d"] == 4
    assert e.scope["e"] == 5
    assert e.scope["f"] == 6
    assert "y" not in e.scope


def test_ifexp(e):
    assert e.run("100 if 1 == 1 else 200") == 100
    assert e.run("100 if 1 == 2 else 200") == 200


def test_list(e):
    assert e.run("[1, 2, 3]") == [1, 2, 3]
    e.run("a = [1, 2, 3]")
    assert e.scope["a"] == [1, 2, 3]


def test_name(e):
    assert e.run("int") is int


def test_nameconstant(e):
    assert e.run("True") is True
    assert e.run("False") is False
    assert e.run("None") is None
    e.run("x = True")
    e.run("y = False")
    e.run("z = None")
    assert e.scope["x"] is True
    assert e.scope["y"] is False
    assert e.scope["z"] is None


def test_num(e):
    assert e.run("123") == 123
    e.run("a = 123")
    assert e.scope["a"] == 123


def test_pass(e):
    assert e.run("pass") is None


def test_set(e):
    assert e.run("{1, 1, 2, 3, 3}") == {1, 2, 3}
    e.run("a = {1, 1, 2, 3, 3}")
    assert e.scope["a"] == {1, 2, 3}


def test_slice(e):
    e.scope["obj"] = GetItemSpy()
    e.run("obj[10:20:3]")
    s = e.scope["obj"].queue.pop()
    assert isinstance(s, slice)
    assert s.start == 10
    assert s.stop == 20
    assert s.step == 3


def test_str(e):
    assert e.run('"asdf"') == "asdf"
    e.run('a = "asdf"')
    assert e.scope["a"] == "asdf"


def test_subscript(e):
    assert e.run("[10, 20, 30][0]") == 10
    assert e.run("(100, 200, 300)[0]") == 100
    assert e.run('{"a": 1000, "b": 2000, "c": 3000}["a"]') == 1000
    e.run("a = [10, 20, 30][0]")
    e.run("b = (100, 200, 300)[0]")
    e.run('c = {"a": 1000, "b": 2000, "c": 3000}["a"]')
    assert e.scope["a"] == 10
    assert e.scope["b"] == 100
    assert e.scope["c"] == 1000
    e.scope["l"] = [11, 22, 33]
    assert e.run("l[2]") == 33
    e.run("l[2] = 44")
    assert e.scope["l"] == [11, 22, 44]
    err = "'int' object is not subscriptable"
    with pytest.raises(NotSubscriptableError, match=err):
        e.run("1[2]")


def test_tuple(e):
    assert e.run("(1, 1, 2, 3, 3)") == (1, 1, 2, 3, 3)
    e.run("a = (1, 1, 2, 3, 3)")
    assert e.scope["a"] == (1, 1, 2, 3, 3)

    assert e.run("()") == ()
    e.run("b = ()")
    assert e.scope["b"] == ()
