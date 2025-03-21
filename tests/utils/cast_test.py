from typing import Any
from typing import NewType
from typing import TypeVar

import pytest
from attrs import define

from yui.utils.attrs import field_transformer
from yui.utils.cast import cast
from yui.utils.cast import is_container


def test_is_container():
    assert is_container(list[int])
    assert is_container(set[int])
    assert is_container(tuple[int])
    assert is_container(list)
    assert is_container(set)
    assert is_container(tuple)
    assert not is_container(int)
    assert not is_container(float)
    assert not is_container(bool)


@define(kw_only=True, field_transformer=field_transformer)
class UserRecord:
    id: str
    pw: str


def test_cast(bot):
    ID = NewType("ID", str)
    N = TypeVar("N", int, float)
    T = TypeVar("T")
    W = TypeVar("W", int, str)

    assert cast(bool, 1) is True
    assert cast(bool, 0) is False
    assert cast(type(None), 0) is None
    assert cast(int, "3") == 3
    assert cast(list[str], ("kirito", "eugeo")) == ["kirito", "eugeo"]
    assert cast(list[int], ("1", "2", "3")) == [1, 2, 3]
    assert cast(tuple[int, float, str], ["1", "2", "3"]) == (1, 2.0, "3")
    assert cast(set[int], ["1", "1", "2"]) == {1, 2}
    assert cast(int | None, 3) == 3
    assert cast(int | None, None) is None
    assert cast(int | float, "3.2") == 3.2
    assert cast(int | str, "e") == "e"
    assert cast(list[ID], [1, 2, 3]) == [ID("1"), ID("2"), ID("3")]
    assert cast(list[N], [1, 2, 3]) == [1, 2, 3]
    assert cast(list[T], [1, 2, 3]) == [1, 2, 3]
    assert cast(list[W], ["e"]) == ["e"]
    assert cast(dict[str, Any], {1: 1, 2: 2.2}) == {"1": 1, "2": 2.2}
    assert cast(dict[str, str], {1: 1, 2: 2.2}) == {"1": "1", "2": "2.2"}
    assert cast(list, ("kirito", "eugeo", 0)) == ["kirito", "eugeo", 0]
    assert cast(tuple, ["1", 2, 3.0]) == ("1", 2, 3.0)
    assert cast(set, ["1", 2, 3.0, 2]) == {"1", 2, 3.0}
    assert cast(
        dict,
        [("1p", "kirito"), ("2p", "eugeo"), ("boss", "admin")],
    ) == {
        "1p": "kirito",
        "2p": "eugeo",
        "boss": "admin",
    }
    user = cast(UserRecord, {"id": "item4", "pw": "supersecret"})
    assert user.id == "item4"
    assert user.pw == "supersecret"
    users = cast(
        list[UserRecord],
        [
            {"id": "item4", "pw": "supersecret"},
            {"id": "item2", "pw": "weak", "addresses": [1, 2]},
        ],
    )
    assert users[0].id == "item4"
    assert users[0].pw == "supersecret"
    assert users[1].id == "item2"
    assert users[1].pw == "weak"

    with pytest.raises(ValueError):
        cast(int | float, "asdf")

    with pytest.raises(ValueError):
        cast(N, "asdf")
