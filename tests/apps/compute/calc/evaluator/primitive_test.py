import pytest

from yui.apps.compute.calc.exceptions import UnavailableTypeError
from yui.apps.compute.calc.types import Decimal as D


def test_bytes(e):
    assert e.run('b""') == b""
    assert e.run('b"asdf"') == b"asdf"


def test_bytes_decimal_mode(ed):
    assert ed.run('b""') == b""
    assert ed.run('b"asdf"') == b"asdf"


def test_complex(e):
    with pytest.raises(
        UnavailableTypeError,
        match="'complex' type is unavailable",
    ):
        e.run("1j")


def test_complex_decimal_mode(ed):
    with pytest.raises(
        UnavailableTypeError,
        match="'complex' type is unavailable",
    ):
        ed.run("1j")


def test_dict(e):
    assert e.run("{}") == {}
    assert e.run("{1: 111, 2: 222}") == {1: 111, 2: 222}


def test_dict_decimal_mode(ed):
    assert ed.run("{}") == {}
    assert ed.run("{1: 111, 2: 222}") == {D(1): D(111), D(2): D(222)}


def test_list(e):
    assert e.run("[]") == []
    assert e.run("[1, 2, 3]") == [1, 2, 3]


def test_list_decimal_mode(ed):
    assert ed.run("[]") == []
    assert ed.run("[1, 2, 3]") == [D(1), D(2), D(3)]


def test_nameconstant(e):
    assert e.run("True") is True
    assert e.run("False") is False
    assert e.run("None") is None
    assert e.run("...") is Ellipsis


def test_nameconstant_decimal_mode(ed):
    assert ed.run("True") is True
    assert ed.run("False") is False
    assert ed.run("None") is None
    assert ed.run("...") is Ellipsis


def test_num(e):
    assert e.run("123") == 123
    assert e.run("123.45") == 123.45


def test_num_decimal_mode(ed):
    assert ed.run("123") == D(123)
    assert ed.run("123.45") == D("123.45")


def test_set(e):
    assert e.run("{1, 1, 2, 3, 3}") == {1, 2, 3}


def test_set_decimal_mode(ed):
    assert ed.run("{1, 1, 2, 3, 3}") == {D(1), D(2), D(3)}


def test_str(e):
    empty = e.run('""')
    assert isinstance(empty, str)
    assert not empty
    assert e.run('"asdf"') == "asdf"


def test_str_decimal_mode(ed):
    empty = ed.run('""')
    assert isinstance(empty, str)
    assert not empty
    assert ed.run('"asdf"') == "asdf"


def test_tuple(e):
    assert e.run("()") == ()
    assert e.run("(1, 1, 2, 3, 3)") == (1, 1, 2, 3, 3)


def test_tuple_decimal_mode(ed):
    assert ed.run("()") == ()
    assert ed.run("(1, 1, 2, 3, 3)") == (D(1), D(1), D(2), D(3), D(3))
