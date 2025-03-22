import math

import pytest

from yui.apps.compute.calc.commands import body
from yui.apps.compute.calc.commands import calc_decimal
from yui.apps.compute.calc.commands import calc_decimal_on_change
from yui.apps.compute.calc.commands import calc_num
from yui.apps.compute.calc.commands import calc_num_on_change
from yui.apps.compute.calc.commands import calculate
from yui.apps.compute.calc.types import Decimal as D
from yui.types.base import Ts
from yui.types.objects import MessageMessage


@pytest.mark.anyio
async def test_calc_decimal_command(bot):
    event = bot.create_message()
    raw = ""
    await calc_decimal(bot, event, raw)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"].startswith("사용법: ")


@pytest.mark.anyio
async def test_calc_decimal_on_change_command(bot, user_id):
    event = bot.create_message(
        message=MessageMessage(user=user_id, ts=Ts("1234.5678")),
    )
    raw = ""
    await calc_decimal_on_change(bot, event, raw)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"].startswith("사용법: ")


@pytest.mark.anyio
async def test_calc_num_command(bot):
    event = bot.create_message()
    raw = ""
    await calc_num(bot, event, raw)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"].startswith("사용법: ")


@pytest.mark.anyio
async def test_calc_num_on_change_command(bot, user_id):
    event = bot.create_message(
        message=MessageMessage(user=user_id, ts=Ts("1234.5678")),
    )
    raw = ""
    await calc_num_on_change(bot, event, raw)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"].startswith("사용법: ")


@pytest.mark.anyio
async def test_command_empty_expr(bot):
    event = bot.create_message()
    expr = "  "
    help_text = "expected"
    await body(bot=bot, event=event, expr=expr, help=help_text)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"] == help_text


@pytest.mark.anyio
async def test_command_bad_syntax(bot):
    event = bot.create_message()
    expr = "1++"
    help_text = "help"
    await body(bot=bot, event=event, expr=expr, help=help_text)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"].startswith(
        "입력해주신 수식에 문법 오류가 있어요! ",
    )


@pytest.mark.anyio
async def test_command_runtime_error(bot):
    event = bot.create_message()
    expr = "await breath()"
    help_text = "help"
    await body(bot=bot, event=event, expr=expr, help=help_text)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert (
        said.data["text"]
        == "입력해주신 수식을 처리할 수 없어요!\n*UnavailableSyntaxError*: `Evaluation of 'Await' node is unavailable.`"
    )


@pytest.mark.anyio
async def test_command_zero_division(bot):
    event = bot.create_message()
    expr = "1/0"
    help_text = "help"
    await body(bot=bot, event=event, expr=expr, help=help_text)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert (
        said.data["text"]
        == "입력해주신 수식은 계산하다보면 0으로 나누기가 발생해서 계산할 수 없어요!"
    )


@pytest.mark.anyio
async def test_command_timeout(bot):
    event = bot.create_message()
    expr = "2**1000"
    help_text = "help"
    await body(bot=bot, event=event, expr=expr, help=help_text, timeout=0.0001)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert (
        said.data["text"]
        == "입력해주신 수식을 계산하려고 했지만 연산 시간이 너무 길어서 중단했어요!"
    )


@pytest.mark.anyio
async def test_command_unexpected_error(bot):
    event = bot.create_message()
    expr = "undefined_variable"
    help_text = "help"
    await body(bot=bot, event=event, expr=expr, help=help_text)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"].startswith(
        "예기치 않은 에러가 발생했어요! NameError",
    )


@pytest.mark.anyio
async def test_command_short_expr(bot):
    event = bot.create_message()
    expr = "1+2"
    help_text = "help"
    await body(bot=bot, event=event, expr=expr, help=help_text)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"] == "`1+2` == `3`"


@pytest.mark.anyio
async def test_command_short_expr_empty_result(bot):
    event = bot.create_message()
    expr = "''"
    help_text = "help"
    await body(bot=bot, event=event, expr=expr, help=help_text)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"] == "`''` == _Empty_"


@pytest.mark.anyio
async def test_command_multiline_expr(bot):
    event = bot.create_message()
    expr = "1+\\\n2"
    help_text = "help"
    await body(bot=bot, event=event, expr=expr, help=help_text)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert (
        said.data["text"] == "*Input*\n```\n1+\\\n2\n```\n*Output*\n```\n3\n```"
    )


@pytest.mark.anyio
async def test_command_multiline_expr_empty_result(bot):
    event = bot.create_message()
    expr = "'''\n'''[1:]"
    help_text = "help"
    await body(
        bot=bot,
        event=event,
        expr=expr,
        help=help_text,
        decimal_mode=False,
    )

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"] == f"*Input*\n```\n{expr}\n```\n*Output*\n_Empty_"


@pytest.mark.anyio
async def test_command_locals(bot):
    event = bot.create_message()
    expr = "sao = '키리토'"
    help_text = "help"
    await body(
        bot=bot,
        event=event,
        expr=expr,
        help=help_text,
        decimal_mode=False,
    )

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert (
        said.data["text"]
        == f"*Input*\n```\n{expr}\n```\n*Local State*\n```\nsao = '키리토'\n```"
    )


@pytest.mark.anyio
async def test_command_none(bot):
    event = bot.create_message()
    expr = "None"
    help_text = "help"
    await body(
        bot=bot,
        event=event,
        expr=expr,
        help=help_text,
        decimal_mode=False,
    )

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert (
        said.data["text"]
        == "입력해주신 수식을 계산했지만 아무런 값도 나오지 않았어요!"
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    (
        (
            "expr",
            "expected_decimal_result",
            "expected_num_result",
            "expected_decimal_local",
            "expected_num_local",
        )
    ),
    [
        ("1", D("1"), 1, {}, {}),
        ("1+2", D("3"), 3, {}, {}),
        (
            "0.1+0.1+0.1+0.1+0.1+0.1+0.1+0.1+0.1+0.1",
            D("1"),
            0.1 + 0.1 + 0.1 + 0.1 + 0.1 + 0.1 + 0.1 + 0.1 + 0.1 + 0.1,
            {},
            {},
        ),
        ("1-2", D("-1"), -1, {}, {}),
        ("4*5", D("20"), 20, {}, {}),
        ("1/2", D("0.5"), 0.5, {}, {}),
        ("10%3", D("1"), 1, {}, {}),
        ("2**3", D("8"), 8, {}, {}),
        ("(1+2)**3", D("27"), 27, {}, {}),
        ("max(1,2,3,4,5)", D("5"), 5, {}, {}),
        ("math.floor(3.2)", D("3"), 3, {}, {}),
        ("1+math.e", D(math.e) + D("1"), math.e + 1, {}, {}),
        ("[1,2,3]", [D("1"), D("2"), D("3")], [1, 2, 3], {}, {}),
        (
            "[x*10 for x in [0,1,2]]",
            [D("0"), D("10"), D("20")],
            [0, 10, 20],
            {},
            {},
        ),
        ("(1,2,3)", (D("1"), D("2"), D("3")), (1, 2, 3), {}, {}),
        ("{3,2,10}", {D("2"), D("3"), D("10")}, {2, 3, 10}, {}, {}),
        ("{x%2 for x in [1,2,3,4]}", {D("0"), D("1")}, {0, 1}, {}, {}),
        ('{"ab": 123}', {"ab": D("123")}, {"ab": 123}, {}, {}),
        (
            '{"k"+str(x): x-1 for x in [1,2,3]}',
            {"k1": D("0"), "k2": D("1"), "k3": D("2")},
            {"k1": 0, "k2": 1, "k3": 2},
            {},
            {},
        ),
        ("3 in [1,2,3]", True, True, {}, {}),
        ("[1,2,3,12,3].count(3)", 2, 2, {}, {}),
        ("sum(range(1, 10, 1))", D("45"), 45, {}, {}),
        ("{1,2} & {2,3}", {D("2")}, {2}, {}, {}),
        ('"item4"', "item4", "item4", {}, {}),
        ('"{}4".format("item")', "item4", "item4", {}, {}),
        ("money = 1000", None, None, {"money": D("1000")}, {"money": 1000}),
        (
            "money = 1000; money * 2",
            D("2000"),
            2000,
            {"money": D("1000")},
            {"money": 1000},
        ),
        (
            'money = 1000; f"{money}원"',
            "1000원",
            "1000원",
            {"money": D("1000")},
            {"money": 1000},
        ),
        (
            "a = 11;\nif a > 10:\n    a += 100\na",
            D("111"),
            111,
            {"a": D(111)},
            {"a": 111},
        ),
    ],
)
async def test_calculate_fine(
    bot,
    expr: str,
    expected_decimal_result,
    expected_num_result,
    expected_decimal_local: dict,
    expected_num_local: dict,
):
    decimal_result, decimal_local = await bot.run_in_other_process(
        calculate,
        expr,
        decimal_mode=True,
    )

    num_result, num_local = await bot.run_in_other_process(
        calculate,
        expr,
        decimal_mode=False,
    )

    assert expected_decimal_result == decimal_result
    assert set(expected_decimal_local.keys()) == set(decimal_local.keys())

    for key in decimal_local:
        expected = expected_decimal_local[key]
        local = decimal_local[key]

        assert type(expected) is type(local)

        if callable(expected):
            assert expected(1) == local(1)
        else:
            assert expected == local

    assert expected_num_result == num_result
    assert set(expected_num_local.keys()) == set(num_local.keys())

    for key in num_local:
        expected = expected_num_local[key]
        local = num_local[key]

        assert type(expected) is type(local)

        assert expected == local
