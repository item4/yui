from yui.apps.compute.calc.types import Decimal as D


def test_decimal():
    assert -D("1") == D("-1")
    assert +D("1") == D("1")
    assert abs(D("-1")) == D("1")
    assert D("1") + 1 == D("2")
    assert 1 + D("1") == D("2")
    assert D("1") - 1 == D("0")
    assert 1 - D("1") == D("0")
    assert D("2") * 3 == D("6")
    assert 2 * D("3") == D("6")
    assert D("10") // 2 == D("5")
    assert 10 // D("2") == D("5")
    assert D("10") / 2.5 == D("4")
    assert 10 / D("2.5") == D("4")
    assert D("5") % 2 == D("1")
    assert 5 % D("2") == D("1")
    assert divmod(D("5"), 2) == (D("2"), D("1"))
    assert divmod(5, D("2")) == (D("2"), D("1"))
    assert D("3") ** 2 == D("9")
    assert 3 ** D("2") == D("9")
    assert pow(D("3"), D("2"), 2) == D("1")
