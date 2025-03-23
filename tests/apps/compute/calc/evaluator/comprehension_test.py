import pytest

from yui.apps.compute.calc.exceptions import AsyncComprehensionError
from yui.apps.compute.calc.exceptions import NotIterableError


def test_dictcomp(e):
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

    err = "Async syntax with 'DictComp' node is unavailable."
    with pytest.raises(AsyncComprehensionError, match=err):
        e.run("{k: v async for k, v in magic}")


def test_listcomp_simple(e):
    assert e.run("[x ** 2 for x in [1, 2, 3]]") == [1, 4, 9]
    assert "x" not in e.scope


def test_listcomp_nested(e):
    assert e.run("[x ** 2 + y for x in [1, 2, 3] for y in [10, 20, 30]]") == (
        [x**2 + y for x in [1, 2, 3] for y in [10, 20, 30]]
    )
    assert "x" not in e.scope
    assert "y" not in e.scope


def test_listcomp_nested_complex(e):
    assert e.run("[y ** 2 for x in [1, 2, 3] for y in [x+1, x+3, x+5]]") == (
        [y**2 for x in [1, 2, 3] for y in [x + 1, x + 3, x + 5]]
    )
    assert "x" not in e.scope
    assert "y" not in e.scope


def test_listcomp_nested_complex_scope_check(e):
    e.scope["x"] = "test x"
    e.scope["y"] = "test y"
    assert e.run("[y ** 2 for x in [1, 2, 3] for y in [x+1, x+3, x+5]]") == (
        [y**2 for x in [1, 2, 3] for y in [x + 1, x + 3, x + 5]]
    )
    assert e.scope["x"] == "test x"
    assert e.scope["y"] == "test y"


def test_listcomp_nested_ifs(e):
    assert e.run(
        "[x + y for x in [1, 2, 3] for y in [11, 22, 33] if x % 2 == 0 if y % 2 == 1]",
    ) == [13, 35]
    assert "x" not in e.scope
    assert "y" not in e.scope


def test_listcomp_nested_ifs_scope_check(e):
    e.scope["x"] = "test x"
    e.scope["y"] = "test y"
    assert e.run(
        "[x + y for x in [1, 2, 3] for y in [11, 22, 33] if x % 2 == 0 if y % 2 == 1]",
    ) == [13, 35]
    assert e.scope["x"] == "test x"
    assert e.scope["y"] == "test y"


def test_listcomp_not_iterable(e):
    err = "'NoneType' object is not iterable"
    with pytest.raises(NotIterableError, match=err):
        e.run("[x for x in None]")
    assert "x" not in e.scope


def test_listcomp_async(e):
    err = "Async syntax with 'ListComp' node is unavailable."
    with pytest.raises(AsyncComprehensionError, match=err):
        e.run("[x async for x in magic]")
    assert "x" not in e.scope


def test_listcomp_async_nested(e):
    err = "Async syntax with 'ListComp' node is unavailable."
    with pytest.raises(AsyncComprehensionError, match=err):
        e.run("[x + y for y in [1, 2, 3] async for x in magic]")
    assert "x" not in e.scope
    assert "y" not in e.scope


def test_setcomp_simple(e):
    assert e.run("{x ** 2 for x in [1, 2, 3, 3]}") == {1, 4, 9}
    assert "x" not in e.scope


def test_setcomp_nested(e):
    assert e.run("{x ** 2 + y for x in [1, 2, 3] for y in [10, 20, 30]}") == (
        {x**2 + y for x in [1, 2, 3] for y in [10, 20, 30]}
    )
    assert "x" not in e.scope
    assert "y" not in e.scope


def test_setcomp_nested_complex(e):
    assert e.run("{y ** 2 for x in [1, 2, 3] for y in [x+1, x+3, x+5]}") == (
        {y**2 for x in [1, 2, 3] for y in [x + 1, x + 3, x + 5]}
    )
    assert "x" not in e.scope
    assert "y" not in e.scope


def test_setcomp_nested_complex_scope_check(e):
    e.scope["x"] = "test x"
    e.scope["y"] = "test y"
    assert e.run("{y ** 2 for x in [1, 2, 3] for y in [x+1, x+3, x+5]}") == (
        {y**2 for x in [1, 2, 3] for y in [x + 1, x + 3, x + 5]}
    )
    assert e.scope["x"] == "test x"
    assert e.scope["y"] == "test y"


def test_setcomp_nested_ifs(e):
    assert e.run(
        "{x + y for x in [1, 2, 3] for y in [11, 22, 33] if x % 2 == 0 if y % 2 == 1}",
    ) == {13, 35}
    assert "x" not in e.scope
    assert "y" not in e.scope


def test_setcomp_nested_ifs_scope_check(e):
    e.scope["x"] = "test x"
    e.scope["y"] = "test y"
    assert e.run(
        "{x + y for x in [1, 2, 3] for y in [11, 22, 33] if x % 2 == 0 if y % 2 == 1}",
    ) == {13, 35}
    assert e.scope["x"] == "test x"
    assert e.scope["y"] == "test y"


def test_setcomp_not_iterable(e):
    err = "'NoneType' object is not iterable"
    with pytest.raises(NotIterableError, match=err):
        e.run("{x for x in None}")
    assert "x" not in e.scope


def test_setcomp_async(e):
    err = "Async syntax with 'SetComp' node is unavailable."
    with pytest.raises(AsyncComprehensionError, match=err):
        e.run("{x async for x in magic}")
    assert "x" not in e.scope


def test_setcomp_async_nested(e):
    err = "Async syntax with 'SetComp' node is unavailable."
    with pytest.raises(AsyncComprehensionError, match=err):
        e.run("{x + y for y in [1, 2, 3] async for x in magic}")
    assert "x" not in e.scope
    assert "y" not in e.scope
