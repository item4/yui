import pytest

from yui.apps.compute.calc.exceptions import UnavailableSyntaxError


def test_annassign(e):
    err = "Evaluation of 'AnnAssign' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run("a: int = 10")

    assert "a" not in e.scope


def test_assert(e):
    err = "Evaluation of 'Assert' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run("assert True")

    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run("assert False")


def test_asyncfor(e):
    e.scope["r"] = 0
    err = "Evaluation of 'AsyncFor' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run(
            """\
async for x in [1, 2, 3, 4]:
    r += x

""",
        )
    assert e.scope["r"] == 0
    assert "x" not in e.scope


def test_asyncfunctiondef(e):
    err = "Evaluation of 'AsyncFunctionDef' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run(
            """\
async def abc():
    pass

""",
        )
    assert "abc" not in e.scope


def test_asyncwith(e):
    e.scope["r"] = 0
    err = "Evaluation of 'AsyncWith' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run(
            """\
async with x() as y:
    r += 100 + y

""",
        )
    assert e.scope["r"] == 0
    assert "y" not in e.scope


def test_await(e):
    err = "Evaluation of 'Await' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run("r = await x()")
    assert "r" not in e.scope


def test_classdef(e):
    err = "Evaluation of 'ClassDef' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run(
            """\
class ABCD:
    pass

""",
        )
    assert "ABCD" not in e.scope

    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run(
            """\
class MyStr(str):
    pass

""",
        )
    assert "MyStr" not in e.scope


def test_functiondef(e):
    err = "Evaluation of 'FunctionDef' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run(
            """\
def abc():
    pass

""",
        )
    assert "abc" not in e.scope


def test_generator_exp(e):
    e.scope["r"] = [1, 2, 3]
    err = "Evaluation of 'GeneratorExp' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run("x = (i ** 2 for i in r)")
    assert "i" not in e.scope
    assert "x" not in e.scope


def test_async_generator_exp(e):
    e.scope["r"] = [1, 2, 3]
    err = "Evaluation of 'GeneratorExp' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run("x = (i ** 2 async for i in r)")
    assert "i" not in e.scope
    assert "x" not in e.scope


def test_global(e):
    err = "Evaluation of 'Global' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run("global x")

    assert "x" not in e.scope


def test_import(e):
    err = "Evaluation of 'Import' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run("import sys")
    assert "sys" not in e.scope

    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run("import numpy as np")
    assert "np" not in e.scope


def test_importfrom(e):
    err = "Evaluation of 'ImportFrom' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run("from os import path")
    assert "path" not in e.scope

    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run("from decimal import Decimal as D")
    assert "D" not in e.scope


def test_lambda(e):
    err = "Evaluation of 'Lambda' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run("lambda x: x*2")
    assert "x" not in e.scope


def test_match(e):
    e.scope["age"] = 10
    err = "Evaluation of 'Match' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run(
            """\
match age:
    case 10:
        x = 1
""",
        )

    assert "x" not in e.scope


def test_namedexpr(e):
    err = "Evaluation of 'NamedExpr' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run(
            """\
if age := 10:
    pass
""",
        )
    assert "age" not in e.scope


def test_nonlocal(e):
    err = "Evaluation of 'Nonlocal' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run("nonlocal x")


def test_raise(e):
    err = "Evaluation of 'Raise' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run("raise NameError")

    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run("raise NameError from exc")


def test_return(e):
    err = "Evaluation of 'Return' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run("return True")


def test_try(e):
    err = "Evaluation of 'Try' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run(
            """\
try:
    x = 1
except:
    pass
""",
        )
    assert "x" not in e.scope


def test_trystar(e):
    err = "Evaluation of 'TryStar' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run(
            """\
try:
    x = 1
except* Exception:
    pass
""",
        )
    assert "x" not in e.scope


def test_typealias(e):
    err = "Evaluation of 'TypeAlias' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run(
            """\
type Number = int
""",
        )
    assert "Number" not in e.scope


def test_with(e):
    err = "Evaluation of 'With' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run(
            """\
with some as s:
    x = 1 + s
""",
        )
    assert "s" not in e.scope
    assert "x" not in e.scope


def test_yield(e):
    err = "Evaluation of 'Yield' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run("x = yield f()")
    assert "x" not in e.scope


def test_yield_from(e):
    err = "Evaluation of 'YieldFrom' node is unavailable."
    with pytest.raises(UnavailableSyntaxError, match=err):
        e.run("x = yield from f()")
    assert "x" not in e.scope
