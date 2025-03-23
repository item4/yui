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
    total = total + x
    if total > 10:
        continue
    total = total * 2
else:
    total = total + 10000
"""
    real_locals = {}
    exec(code, locals=real_locals)  # noqa: S102 - for test only
    e.run(code)
    assert e.scope["total"] == real_locals["total"]
    assert e.current_interrupt is None


def test_for_break(e):
    code = """\
total = 0
for x in [1, 2, 3, 4, 5, 6]:
    total = total + x
    if total > 10:
        break
    total = total * 2
else:
    total = total + 10000
"""
    real_locals = {}
    exec(code, locals=real_locals)  # noqa: S102 - for test only
    e.run(code)
    assert e.scope["total"] == real_locals["total"]
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


def test_while(e):
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
