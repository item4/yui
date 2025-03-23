import ast

import pytest

from yui.apps.compute.calc.exceptions import NotIterableError


def test_break(e):
    e.run("break")
    assert isinstance(e.current_interrupt, ast.Break)


def test_continue(e):
    e.run("continue")
    assert isinstance(e.current_interrupt, ast.Continue)


def test_for_continue(e):
    code = """\
total = 0
for x in [1, 2, 3, 4, 5, 6]:
    total += x
    if total > 10:
        continue
    total *= 2
else:
    check = 100
"""
    real_locals = {}
    exec(code, locals=real_locals)  # noqa: S102 - for test only
    e.run(code)
    assert e.scope["x"] == real_locals["x"] == 6
    assert e.scope["total"] == real_locals["total"] == 26
    assert e.scope["check"] == real_locals["check"] == 100
    assert e.current_interrupt is None


def test_for_break(e):
    code = """\
total = 0
for x in [1, 2, 3, 4, 5, 6]:
    total += x
    if total > 10:
        break
    total *= 2
else:
    check = 100
"""
    real_locals = {}
    exec(code, locals=real_locals)  # noqa: S102 - for test only
    e.run(code)
    assert e.scope["x"] == real_locals["x"] == 3
    assert e.scope["total"] == real_locals["total"] == 11
    assert "check" not in e.scope
    assert e.current_interrupt is None


def test_for_empty(e):
    code = """\
total = 0
for x in []:
    total += x
else:
    check = 100
"""
    real_locals = {}
    exec(code, locals=real_locals)  # noqa: S102 - for test only
    e.run(code)
    assert "x" not in e.scope
    assert e.scope["total"] == real_locals["total"] == 0
    assert e.scope["check"] == real_locals["check"] == 100
    assert e.current_interrupt is None


def test_for_nested(e):
    code = """\
selected = []
names = ["kirito", "eugeo", "asuna", "sinon"]
for name in names:
    for x in name:
        if x == "n":
            break
    else:
        selected.append(name)
else:
    check = 100
"""
    real_locals = {}
    exec(code, locals=real_locals)  # noqa: S102 - for test only
    e.run(code)
    assert e.scope["selected"] == real_locals["selected"] == ["kirito", "eugeo"]
    assert (
        e.scope["names"]
        == real_locals["names"]
        == ["kirito", "eugeo", "asuna", "sinon"]
    )
    assert e.scope["name"] == real_locals["name"] == "sinon"
    assert e.scope["x"] == real_locals["x"] == "n"
    assert e.scope["check"] == real_locals["check"] == 100
    assert e.current_interrupt is None


def test_for_not_iterable(e):
    err = "'NoneType' object is not iterable"
    with pytest.raises(NotIterableError, match=err):
        e.run(
            """\
for x in None:
    pass
""",
        )

    assert "x" not in e.scope
    assert e.current_interrupt is None


def test_while_simple(e):
    code = """\
total = 0
i = 1
while total > 100:
    total += i
    i *= 2
"""
    real_locals = {}
    exec(code, locals=real_locals)  # noqa: S102 - for test only
    e.run(code)
    assert e.scope["total"] == real_locals["total"]
    assert e.current_interrupt is None


def test_while_orelse(e):
    code = """\
total = 0
i = 1
while total > 100:
    total += i
    i *= 2
else:
    total += 10000
    check = 100
"""
    real_locals = {}
    exec(code, locals=real_locals)  # noqa: S102 - for test only
    e.run(code)
    assert e.scope["total"] == real_locals["total"]
    assert e.scope["check"] == real_locals["check"] == 100
    assert e.current_interrupt is None


def test_while_continue(e):
    code = """\
length = 0
data = list("kirito")
while data:
    x = data.pop()
    if x in {"a", "e", "i", "o", "u"}:
        continue
    length += 1
else:
    check = 100
"""
    real_locals = {}
    exec(code, locals=real_locals)  # noqa: S102 - for test only
    e.run(code)
    assert e.scope["length"] == real_locals["length"] == 3
    assert e.scope["check"] == real_locals["check"] == 100
    assert e.current_interrupt is None


def test_while_break(e):
    code = """\
r = 0
while True:
    break
else:
    r += 10
    check = 100
"""
    real_locals = {}
    exec(code, locals=real_locals)  # noqa: S102 - for test only
    e.run(code)
    assert e.scope["r"] == real_locals["r"] == 0
    assert "check" not in e.scope
    assert e.current_interrupt is None


def test_while_never(e):
    code = """\
r = 0
while False:
    r += 100
    x = 999
else:
    r += 10
    check = 100
"""
    real_locals = {}
    exec(code, locals=real_locals)  # noqa: S102 - for test only
    e.run(code)
    assert e.scope["r"] == real_locals["r"] == 10
    assert e.scope["check"] == real_locals["check"] == 100
    assert "x" not in e.scope
    assert e.current_interrupt is None


def test_while_nested(e):
    code = """\
selected = []
names = ["kirito", "eugeo", "asuna", "sinon"]
while names:
    name = names.pop()
    chunks = list(name)
    while chunks:
        x = chunks.pop()
        if x == "n":
            break
    else:
        selected.append(name)
else:
    check = 100
"""
    real_locals = {}
    exec(code, locals=real_locals)  # noqa: S102 - for test only
    e.run(code)
    assert e.scope["selected"] == real_locals["selected"] == ["eugeo", "kirito"]
    assert e.scope["names"] == real_locals["names"] == []
    assert e.scope["name"] == real_locals["name"] == "kirito"
    assert e.scope["chunks"] == real_locals["chunks"] == []
    assert e.scope["x"] == real_locals["x"] == "k"
    assert e.scope["check"] == real_locals["check"] == 100
    assert e.current_interrupt is None
