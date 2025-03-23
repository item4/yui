import re

import pytest

from yui.apps.compute.calc.types import Decimal as D


def test_binop(e):
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


def test_boolop(e):
    assert e.run("True and False") is (True and False)  # noqa: SIM223
    assert e.run("True or False") is (True or False)  # noqa: SIM222


def test_unaryop(e):
    assert e.run("~100") == ~100
    assert e.run("not 100") == (not 100)
    assert e.run("+100") == +100
    assert e.run("-100") == -100


def test_binop_decimal(ed):
    error_format = (
        "unsupported operand type(s) for {op}: 'Decimal' and 'Decimal'"
    )
    with pytest.raises(TypeError, match=re.escape(error_format.format(op="&"))):
        ed.run("3 & 2")

    with pytest.raises(TypeError, match=re.escape(error_format.format(op="|"))):
        ed.run("1 | 2")

    with pytest.raises(TypeError, match=re.escape(error_format.format(op="^"))):
        assert ed.run("3 ^ 2")

    with pytest.raises(
        TypeError,
        match=re.escape(error_format.format(op="<<")),
    ):
        ed.run("3 << 2")

    with pytest.raises(TypeError, match=re.escape(error_format.format(op="@"))):
        ed.run("2 @ 3")

    with pytest.raises(
        TypeError,
        match=re.escape(error_format.format(op=">>")),
    ):
        ed.run("100 >> 2")

    assert ed.run("1 + 2") == D(1) + D(2)
    assert ed.run("3 / 2") == D(3) / D(2)
    assert ed.run("3 // 2") == D(3) // D(2)
    assert ed.run("3 * 2") == D(3) * D(2)
    assert ed.run("33 % 4") == D(33) % D(4)
    assert ed.run("3 ** 2") == D(3) ** D(2)
    assert ed.run("3 - 1") == D(3) - D(1)


def test_boolop_decimal(ed):
    assert ed.run("True and False") is (True and False)  # noqa: SIM223
    assert ed.run("True or False") is (True or False)  # noqa: SIM222


def test_unaryop_decimal(ed):
    with pytest.raises(
        TypeError,
        match="bad operand type for unary ~: 'Decimal'",
    ):
        ed.run("~100")
    assert ed.run("not 100") == (not D(100))
    assert ed.run("+100") == +D(100)
    assert ed.run("-100") == -D(100)
