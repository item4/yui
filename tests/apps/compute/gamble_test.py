import pytest

from yui.apps.compute.gamble import dice
from yui.apps.compute.gamble import parse_dice_syntax


def test_parse_dice_syntax():
    with pytest.raises(SyntaxError) as e:
        parse_dice_syntax("d2 " * 10)
    assert str(e.value) == "Too many queries"

    with pytest.raises(SyntaxError) as e:
        parse_dice_syntax("bug")
    assert str(e.value) == "Can not parse this chunk (`bug`)"

    with pytest.raises(SyntaxError) as e:
        parse_dice_syntax("0d6")
    assert str(e.value) == "Number of dice must be larger than 0"

    with pytest.raises(SyntaxError) as e:
        parse_dice_syntax("20d6")
    assert str(e.value) == "YOU JUST ACTIVATED COUNT TRAP CARD!"

    with pytest.raises(SyntaxError) as e:
        parse_dice_syntax("d1")
    assert str(e.value) == "Number of faces must be larger than 1"
    with pytest.raises(SyntaxError) as e:
        parse_dice_syntax("d1000")
    assert str(e.value) == "YOU JUST ACTIVATED FACES TRAP CARD!"

    result = parse_dice_syntax("1d6+0", seed=100)
    assert result[0].query == "d6"
    assert result[0].result == "2"

    result = parse_dice_syntax("2d6+2", seed=200)
    assert result[0].query == "2d6+2"
    assert result[0].result == "5 (1+2+2)"

    result = parse_dice_syntax("2d6-2", seed=300)
    assert result[0].query == "2d6-2"
    assert result[0].result == "6 (5+3-2)"


@pytest.mark.anyio
async def test_dice_handler(bot):
    event = bot.create_message()

    assert not await dice(bot, event, "", seed=100)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["username"] == "딜러"
    assert (
        said.data["text"] == "유이가 기도하며 주사위를 굴려줬습니다. 19입니다."
    )

    assert not await dice(bot, event, "", seed=206)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["username"] == "딜러"
    assert said.data["text"] == "콩"

    assert not await dice(bot, event, "", seed=503)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["username"] == "딜러"
    assert said.data["text"] == "콩콩"

    assert not await dice(bot, event, "bug")

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["username"] == "딜러"
    assert said.data["text"] == "*Error*: Can not parse this chunk (`bug`)"

    assert not await dice(bot, event, "1d6+0", seed=100)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["username"] == "딜러"
    assert said.data["text"] == "d6 == 2"
