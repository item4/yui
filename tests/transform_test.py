import datetime
import enum
from decimal import Decimal

import pytest

from yui.transform import choice
from yui.transform import enum_getitem
from yui.transform import extract_url
from yui.transform import get_channel_id
from yui.transform import get_user_id
from yui.transform import str_to_date
from yui.transform import value_range


def test_str_to_date():
    """Test str_to_date helper."""

    with pytest.raises(ValueError):
        str_to_date()("9999")

    assert str_to_date()("2017-10-07") == datetime.date(2017, 10, 7)
    assert str_to_date()("2017년 10월 7일") == datetime.date(2017, 10, 7)

    with pytest.raises(ValueError):
        str_to_date()("2017-10-99")

    assert str_to_date(datetime.date.today)("2017-10-07") == datetime.date(
        2017,
        10,
        7,
    )
    assert str_to_date(datetime.date.today)("2017년 10월 7일") == datetime.date(
        2017,
        10,
        7,
    )
    assert (
        str_to_date(datetime.date.today)("2017-10-99") == datetime.date.today()
    )


def test_enum_getitem():
    """Test enum_getitem helper."""

    class A(enum.Enum):
        a = 1
        b = 2
        c = 3

    assert enum_getitem(A)("a") == A.a

    with pytest.raises(ValueError):
        enum_getitem(A)("zzz")

    assert enum_getitem(A, fallback="b")("a") == A.a
    assert enum_getitem(A, fallback="b")("zzz") == A.b


def test_extract_url():
    """Test extract_url helper."""

    assert extract_url("https://item4.net") == "https://item4.net"
    assert extract_url("<https://item4.net>") == "https://item4.net"
    assert extract_url("<https://item4.net|innocent>") == "https://item4.net"


def test_get_channel_id(bot):
    """Test get_channel helper."""

    test = bot.create_channel("C1", "test")

    assert get_channel_id("<C1>") == test.id
    assert get_channel_id("<#C1>") == test.id
    assert get_channel_id("<C1|test>") == test.id
    assert get_channel_id("<#C1|test>") == test.id


def test_get_user_id(bot):
    """Test get_user helper."""

    item4 = bot.create_user("U1", "item4")

    assert get_user_id("<U1>") == item4.id
    assert get_user_id("<@U1>") == item4.id
    assert get_user_id("<U1|item4>") == item4.id
    assert get_user_id("<@U1|item4>") == item4.id


@pytest.mark.parametrize(
    "items",
    [["Dog", "cat", "fish"], ("Dog", "cat", "fish")],
)
def test_choice(items):
    assert choice(items)("cat") == "cat"

    with pytest.raises(ValueError):
        choice(items)("bird")

    assert choice(items, fallback="fish")("cat") == "cat"
    assert choice(items, fallback="fish")("bird") == "fish"

    assert choice(items, case_insensitive=True)("cat") == "cat"
    assert choice(items, case_insensitive=True)("dog") == "dog"
    assert choice(items, case_insensitive=True)("Dog") == "Dog"
    assert choice(items, case_insensitive=True)("DOG") == "DOG"

    assert choice(items, case="lower")("cat") == "cat"
    assert choice(items, case="lower")("Dog") == "dog"

    with pytest.raises(ValueError):
        choice(items, case="lower")("DOG")

    assert choice(items, case="lower", fallback="fish")("cat") == "cat"
    assert choice(items, case="lower", fallback="fish")("Dog") == "dog"
    assert choice(items, case="lower", fallback="fish")("bird") == "fish"

    assert choice(items, case="lower", case_insensitive=True)("cat") == "cat"
    assert choice(items, case="lower", case_insensitive=True)("CAT") == "cat"

    assert choice(items, case_insensitive=True)("cat") == "cat"

    with pytest.raises(ValueError):
        choice(items, case_insensitive=True)("bird")

    assert choice(items, fallback="fish", case_insensitive=True)("cat") == "cat"
    assert (
        choice(items, fallback="fish", case_insensitive=True)("bird") == "fish"
    )
    assert choice(items, fallback="fish", case_insensitive=True)("dog") == "dog"
    assert choice(items, fallback="fish", case_insensitive=True)("Dog") == "Dog"
    assert choice(items, fallback="fish", case_insensitive=True)("DOG") == "DOG"


def test_value_range():
    # Decimal
    one = Decimal(1)
    three = Decimal("3.0")
    five = Decimal(5)

    assert value_range(one, five)(three) == Decimal(three)
    assert value_range(one, five, autofix=True)(three) == Decimal(three)

    with pytest.raises(ValueError):
        value_range(one, five)(Decimal("0.0"))

    with pytest.raises(ValueError):
        value_range(one, five)(Decimal("6.0"))

    assert value_range(one, five, autofix=True)(Decimal("0.0")) == one
    assert value_range(one, five, autofix=True)(Decimal("6.0")) == five

    # float

    assert value_range(1.0, 5.0)(3.0) == 3.0
    assert value_range(1.0, 5.0, autofix=True)(3.0) == 3.0

    with pytest.raises(ValueError):
        value_range(1.0, 5.0)(0.0)

    with pytest.raises(ValueError):
        value_range(1.0, 5.0)(6.0)

    assert value_range(1.0, 5.0, autofix=True)(0.0) == 1.0
    assert value_range(1.0, 5.0, autofix=True)(6.0) == 5.0

    # int

    assert value_range(1, 5)(3) == 3
    assert value_range(1, 5, autofix=True)(3) == 3

    with pytest.raises(ValueError):
        value_range(1, 5)(0)

    with pytest.raises(ValueError):
        value_range(1, 5)(6)

    assert value_range(1, 5, autofix=True)(0) == 1
    assert value_range(1, 5, autofix=True)(6) == 5
