import functools
import html
import math
from datetime import date

import pytest

from yui.apps.compute.calc.evaluator import Evaluator
from yui.apps.compute.calc.evaluator import ScopeStack
from yui.apps.compute.calc.exceptions import BadSyntax
from yui.apps.compute.calc.exceptions import NotIterableError
from yui.apps.compute.calc.exceptions import NotSubscriptableError
from yui.apps.compute.calc.exceptions import UnavailableSyntaxError
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


def test_annassign():
    e = Evaluator()

    err = "Evaluation of 'AnnAssign' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run("a: int = 10")

    assert "a" not in e.scope


def test_assert():
    e = Evaluator()
    err = "Evaluation of 'Assert' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run("assert True")

    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run("assert False")


def test_assign():
    e = Evaluator()
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

    err = "cannot unpack non-iterable int object"
    with pytest.raises(TypeError, match=err):
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


def test_asyncfor():
    e = Evaluator()
    e.scope["r"] = 0
    err = "Evaluation of 'AsyncFor' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run(
            """
async for x in [1, 2, 3, 4]:
    r += x

""",
        )
    assert e.scope["r"] == 0


def test_asyncfunctiondef():
    e = Evaluator()
    err = "Evaluation of 'AsyncFunctionDef' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run(
            """
async def abc():
    pass

""",
        )
    assert "abc" not in e.scope


def test_asyncwith():
    e = Evaluator()
    e.scope["r"] = 0
    err = "Evaluation of 'AsyncWith' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run(
            """
async with x():
    r += 100

""",
        )
    assert e.scope["r"] == 0


def test_attribute():
    e = Evaluator()
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


def test_augassign():
    e = Evaluator()
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


def test_await():
    e = Evaluator()
    err = "Evaluation of 'Await' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run("r = await x()")
    assert "r" not in e.scope


def test_binop():
    e = Evaluator()
    assert e.run("1 + 2") == 1 + 2
    assert e.run("3 & 2") == 3 & 2
    assert e.run("1 | 2") == 1 | 2
    assert e.run("3 ^ 2") == 3 ^ 2
    assert e.run("3 / 2") == 3 / 2
    assert e.run("3 // 2") == 3 // 2
    assert e.run("3 << 2") == 3 << 2
    with pytest.raises(TypeError):
        e.run("2 @ 3")
    assert e.run("3 * 2") == 3 * 2
    assert e.run("33 % 4") == 33 % 4
    assert e.run("3 ** 2") == 3**2
    assert e.run("100 >> 2") == 100 >> 2
    assert e.run("3 - 1") == 3 - 1


def test_boolop():
    e = Evaluator()
    assert e.run("True and False") is (True and False)  # noqa: SIM223
    assert e.run("True or False") is (True or False)  # noqa: SIM222


def test_break():
    e = Evaluator()
    e.run("break")
    assert e.current_interrupt.__class__.__name__ == "Break"


def test_bytes():
    e = Evaluator()
    assert e.run('b"asdf"') == b"asdf"
    e.run('a = b"asdf"')
    assert e.scope["a"] == b"asdf"


def test_call():
    e = Evaluator()
    e.scope["date"] = date
    e.run("x = date(2019, 10, day=7)")
    assert e.scope["x"] == date(2019, 10, day=7)

    e.scope["math"] = math
    e.run("y = math.sqrt(121)")
    assert e.scope["y"] == math.sqrt(121)

    e.run("z = html.escape('<hello>')")
    assert e.scope["z"] == html.escape("<hello>")


def test_classdef():
    e = Evaluator()
    err = "Evaluation of 'ClassDef' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run(
            """
class ABCD:
    pass

""",
        )
    assert "ABCD" not in e.scope


def test_compare():
    e = Evaluator()
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


def test_continue():
    e = Evaluator()
    e.run("continue")
    assert e.current_interrupt.__class__.__name__ == "Continue"


def test_delete():
    e = Evaluator()
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


def test_dict():
    e = Evaluator()
    assert e.run("{1: 111, 2: 222}") == {1: 111, 2: 222}
    e.run("a = {1: 111, 2: 222}")
    assert e.scope["a"] == {1: 111, 2: 222}


def test_dictcomp():
    e = Evaluator()
    assert e.run("{k+1: v**2 for k, v in {1: 1, 2: 11, 3: 111}.items()}") == {
        2: 1,
        3: 121,
        4: 12321,
    }
    assert "k" not in e.scope
    assert "v" not in e.scope

    e.run("a = {k+1: v**2 for k, v in {1: 1, 2: 11, 3: 111}.items()}")
    assert e.scope["a"] == {
        2: 1,
        3: 121,
        4: 12321,
    }
    assert "k" not in e.scope
    assert "v" not in e.scope

    e.run("k = 'test k'")
    e.run("v = 'test v'")
    assert e.run("{k+1: v**2 for k, v in {1: 1, 2: 11, 3: 111}.items()}") == {
        2: 1,
        3: 121,
        4: 12321,
    }
    assert e.scope["k"] == "test k"
    assert e.scope["v"] == "test v"

    assert e.run(
        "{k: v for k in [1, 2, 3] for v in [11, 22, 33] if k % 2 == 0 if v % 2 == 1}",
    ) == {2: 33}
    assert e.scope["k"] == "test k"
    assert e.scope["v"] == "test v"

    err = "'NoneType' object is not iterable"
    with pytest.raises(NotIterableError, match=err):
        e.run("{x: x for x in None}")


def test_expr():
    e = Evaluator()
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


def test_functiondef():
    e = Evaluator()
    err = "Evaluation of 'FunctionDef' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run(
            """
def abc():
    pass

""",
        )
    assert "abc" not in e.scope


def test_for():
    code = """\
total = 0
for x in [1, 2, 3, 4, 5, 6]:
    total = total + x
    if total > 10:
        continue
    total = total * 2
else:
    total = total + 10000
"""
    real_locals = {}
    exec(code, locals=real_locals)  # noqa: S102 - for test only
    e = Evaluator()
    e.run(code)
    assert e.scope["total"] == real_locals["total"]

    code = """\
total2 = 0
for x in [1, 2, 3, 4, 5, 6]:
    total2 = total2 + x
    if total2 > 10:
        break
    total2 = total2 * 2
else:
    total2 = total2 + 10000
"""
    real_locals = {}
    exec(code, locals=real_locals)  # noqa: S102 - for test only
    e.run(code)
    assert e.scope["total2"] == real_locals["total2"]

    err = "'NoneType' object is not iterable"
    with pytest.raises(NotIterableError, match=err):
        e.run(
            """\
for x in None:
    pass
""",
        )


def test_formattedvalue():
    e = Evaluator()
    e.scope["before"] = 123456
    e.run('after = f"change {before} to {before:,}!"')
    assert e.scope["after"] == "change 123456 to 123,456!"


def test_generator_exp():
    e = Evaluator()
    e.scope["r"] = [1, 2, 3]
    err = "Evaluation of 'GeneratorExp' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run("x = (i ** 2 for i in r)")
    assert "x" not in e.scope


def test_global():
    e = Evaluator()
    err = "Evaluation of 'Global' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run("global x")


def test_if():
    e = Evaluator()
    e.scope["a"] = 1
    e.run(
        """
if a == 1:
    a = 2
    b = 3
""",
    )
    assert e.scope["a"] == 2
    assert e.scope["b"] == 3

    e.run(
        """
if a == 1:
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

    e.run(
        """
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
""",
    )
    assert e.scope["a"] == 3
    assert e.scope["b"] == 4
    assert e.scope["c"] == 5
    assert e.scope["d"] == 4
    assert e.scope["e"] == 5
    assert e.scope["f"] == 6
    assert "y" not in e.scope
    assert "z" not in e.scope


def test_ifexp():
    e = Evaluator()
    assert e.run("100 if 1 == 1 else 200") == 100
    assert e.run("100 if 1 == 2 else 200") == 200


def test_import():
    e = Evaluator()
    err = "Evaluation of 'Import' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run("import sys")
    assert "sys" not in e.scope


def test_importfrom():
    e = Evaluator()
    err = "Evaluation of 'ImportFrom' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run("from os import path")
    assert "path" not in e.scope


def test_lambda():
    e = Evaluator()
    err = "Evaluation of 'Lambda' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run("lambda x: x*2")


def test_list():
    e = Evaluator()
    assert e.run("[1, 2, 3]") == [1, 2, 3]
    e.run("a = [1, 2, 3]")
    assert e.scope["a"] == [1, 2, 3]


def test_listcomp():
    e = Evaluator()
    assert e.run("[x ** 2 for x in [1, 2, 3]]") == [1, 4, 9]
    assert "x" not in e.scope

    assert e.run("[x ** 2 + y for x in [1, 2, 3] for y in [10, 20, 30]]") == (
        [x**2 + y for x in [1, 2, 3] for y in [10, 20, 30]]
    )
    assert "x" not in e.scope
    assert "y" not in e.scope

    assert e.run("[y ** 2 for x in [1, 2, 3] for y in [x+1, x+3, x+5]]") == (
        [y**2 for x in [1, 2, 3] for y in [x + 1, x + 3, x + 5]]
    )
    assert "x" not in e.scope
    assert "y" not in e.scope

    e.run("x = 'test x'")
    e.run("y = 'test y'")
    assert e.run("[y ** 2 for x in [1, 2, 3] for y in [x+1, x+3, x+5]]") == (
        [y**2 for x in [1, 2, 3] for y in [x + 1, x + 3, x + 5]]
    )
    assert e.scope["x"] == "test x"
    assert e.scope["y"] == "test y"

    assert e.run(
        "[x + y for x in [1, 2, 3] for y in [11, 22, 33] if x % 2 == 0 if y % 2 == 1]",
    ) == [13, 35]
    assert e.scope["x"] == "test x"
    assert e.scope["y"] == "test y"

    err = "'NoneType' object is not iterable"
    with pytest.raises(NotIterableError, match=err):
        e.run("[x for x in None]")


def test_name():
    e = Evaluator()
    assert e.run("int") is int


def test_nameconstant():
    e = Evaluator()
    assert e.run("True") is True
    assert e.run("False") is False
    assert e.run("None") is None
    e.run("x = True")
    e.run("y = False")
    e.run("z = None")
    assert e.scope["x"] is True
    assert e.scope["y"] is False
    assert e.scope["z"] is None


def test_nonlocal():
    e = Evaluator()
    err = "Evaluation of 'Nonlocal' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run("nonlocal x")


def test_num():
    e = Evaluator()
    assert e.run("123") == 123
    e.run("a = 123")
    assert e.scope["a"] == 123


def test_pass():
    e = Evaluator()
    e.run("pass")


def test_raise():
    e = Evaluator()
    err = "Evaluation of 'Raise' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run("raise NameError")


def test_return():
    e = Evaluator()
    err = "Evaluation of 'Return' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run("return True")


def test_set():
    e = Evaluator()
    assert e.run("{1, 1, 2, 3, 3}") == {1, 2, 3}
    e.run("a = {1, 1, 2, 3, 3}")
    assert e.scope["a"] == {1, 2, 3}


def test_setcomp():
    e = Evaluator()
    assert e.run("{x ** 2 for x in [1, 2, 3, 3]}") == {1, 4, 9}
    assert "x" not in e.scope

    assert e.run("{x ** 2 + y for x in [1, 2, 3] for y in [10, 20, 30]}") == (
        {x**2 + y for x in [1, 2, 3] for y in [10, 20, 30]}
    )
    assert "x" not in e.scope
    assert "y" not in e.scope

    assert e.run("{y ** 2 for x in [1, 2, 3] for y in [x+1, x+3, x+5]}") == (
        {y**2 for x in [1, 2, 3] for y in [x + 1, x + 3, x + 5]}
    )
    assert "x" not in e.scope
    assert "y" not in e.scope

    e.run("x = 'test x'")
    e.run("y = 'test y'")
    assert e.run("{y ** 2 for x in [1, 2, 3] for y in [x+1, x+3, x+5]}") == (
        {y**2 for x in [1, 2, 3] for y in [x + 1, x + 3, x + 5]}
    )
    assert e.scope["x"] == "test x"
    assert e.scope["y"] == "test y"

    assert e.run(
        "{x + y for x in [1, 2, 3] for y in [11, 22, 33] if x % 2 == 0 if y % 2 == 1}",
    ) == {13, 35}
    assert e.scope["x"] == "test x"
    assert e.scope["y"] == "test y"

    err = "'NoneType' object is not iterable"
    with pytest.raises(NotIterableError, match=err):
        e.run("{x for x in None}")


def test_slice():
    e = Evaluator()
    e.scope["obj"] = GetItemSpy()
    e.run("obj[10:20:3]")
    s = e.scope["obj"].queue.pop()
    assert isinstance(s, slice)
    assert s.start == 10
    assert s.stop == 20
    assert s.step == 3


def test_str():
    e = Evaluator()
    assert e.run('"asdf"') == "asdf"
    e.run('a = "asdf"')
    assert e.scope["a"] == "asdf"


def test_subscript():
    e = Evaluator()
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


def test_try():
    e = Evaluator()
    err = "Evaluation of 'Try' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run(
            """
try:
    x = 1
except:
    pass
""",
        )
    assert "x" not in e.scope


def test_trystar():
    e = Evaluator()
    err = "Evaluation of 'TryStar' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run(
            """
try:
    x = 1
except* Exception:
    pass
""",
        )
    assert "x" not in e.scope


def test_tuple():
    e = Evaluator()
    assert e.run("(1, 1, 2, 3, 3)") == (1, 1, 2, 3, 3)
    e.run("a = (1, 1, 2, 3, 3)")
    assert e.scope["a"] == (1, 1, 2, 3, 3)


def test_typealias():
    e = Evaluator()
    err = "Evaluation of 'TypeAlias' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run(
            """
type Number = int
""",
        )
    assert "Number" not in e.scope


def test_unaryop():
    e = Evaluator()
    assert e.run("~100") == ~100
    assert e.run("not 100") == (not 100)
    assert e.run("+100") == +100
    assert e.run("-100") == -100


def test_while():
    code = """\
total = 0
i = 1
while total > 100:
    total += i
    i += i
    if i % 10 == 0:
        i += 1
else:
    total = total + 10000
"""
    real_locals = {}
    exec(code, locals=real_locals)  # noqa: S102 - for test only
    e = Evaluator()
    e.run(code)
    assert e.scope["total"] == real_locals["total"]

    code = """\
r = 0
while True:
    break
else:
    r += 10
"""
    real_locals = {}
    exec(code, locals=real_locals)  # noqa: S102 - for test only
    e.run(code)
    assert e.scope["r"] == real_locals["r"]


def test_with():
    e = Evaluator()
    err = "Evaluation of 'With' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run(
            """
with some:
    x = 1
""",
        )
    assert "x" not in e.scope


def test_yield():
    e = Evaluator()
    err = "Evaluation of 'Yield' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run("x = yield f()")
    assert "x" not in e.scope


def test_yield_from():
    e = Evaluator()
    err = "Evaluation of 'YieldFrom' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run("x = yield from f()")
    assert "x" not in e.scope
