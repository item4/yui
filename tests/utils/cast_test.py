from typing import Any
from typing import NewType

import pytest

from yui.utils.attrs import define
from yui.utils.cast import cast


@define
class UserRecord:
    id: str
    pw: str


def test_cast(bot):
    bot.add_user("U1", "kirito")
    bot.add_channel("C1", "general")
    bot.add_channel("C2", "random")
    bot.add_channel("C3", "food")
    bot.add_dm("D1", "U1")
    bot.add_private_channel("G1", "secret")

    ID = NewType("ID", str)

    assert cast(int, "3") == 3
    assert cast(list[str], ("kirito", "asuna")) == ["kirito", "asuna"]
    assert cast(list[int], ("1", "2", "3")) == [1, 2, 3]
    assert cast(tuple[int, float, str], ["1", "2", "3"]) == (1, 2.0, "3")
    assert cast(set[int], ["1", "1", "2"]) == {1, 2}
    assert cast(int | None, 3) == 3
    assert cast(int | None, None) is None
    assert cast(int | float, "3.2") == 3.2
    assert cast(list[ID], [1, 2, 3]) == [ID("1"), ID("2"), ID("3")]
    assert cast(dict[str, Any], {1: 1, 2: 2.2}) == {"1": 1, "2": 2.2}
    assert cast(dict[str, str], {1: 1, 2: 2.2}) == {"1": "1", "2": "2.2"}
    assert cast(list, ("kirito", "asuna", 16.5)) == ["kirito", "asuna", 16.5]
    assert cast(tuple, ["1", 2, 3.0]) == ("1", 2, 3.0)
    assert cast(set, ["1", 2, 3.0, 2]) == {"1", 2, 3.0}
    assert cast(dict, {"1": "kirito", 2: "asuna", 3: 16.5}) == {
        "1": "kirito",
        2: "asuna",
        3: 16.5,
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
