import pytest


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
