import asyncio
import math
from concurrent.futures.process import ProcessPoolExecutor
from datetime import date
from datetime import datetime

import pytest
import pytest_asyncio

from yui.apps.compute.calc import BadSyntax
from yui.apps.compute.calc import Decimal as D
from yui.apps.compute.calc import Evaluator
from yui.apps.compute.calc import ScopeStack
from yui.apps.compute.calc import body
from yui.apps.compute.calc import calc_decimal
from yui.apps.compute.calc import calc_decimal_on_change
from yui.apps.compute.calc import calc_num
from yui.apps.compute.calc import calc_num_on_change
from yui.apps.compute.calc import calculate
from yui.types.objects import MessageMessage

from ...util import FakeBot


class GetItemSpy:
    def __init__(self):
        self.queue = []

    def __getitem__(self, item):
        self.queue.append(item)


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.asyncio
async def test_calc_decimal_command(bot):
    event = bot.create_message("C1", "U1")
    raw = ""
    await calc_decimal(bot, event, raw)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"].startswith("사용법: ")


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.asyncio
async def test_calc_decimal_on_change_command(bot):
    event = bot.create_message(
        "C1",
        "U1",
        message=MessageMessage(user="U1", ts="1234.5678"),
    )
    raw = ""
    await calc_decimal_on_change(bot, event, raw)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"].startswith("사용법: ")


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.asyncio
async def test_calc_num_command(bot):
    event = bot.create_message("C1", "U1")
    raw = ""
    await calc_num(bot, event, raw)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"].startswith("사용법: ")


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.asyncio
async def test_calc_num_on_change_command(bot):
    event = bot.create_message(
        "C1",
        "U1",
        message=MessageMessage(user="U1", ts="1234.5678"),
    )
    raw = ""
    await calc_num_on_change(bot, event, raw)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"].startswith("사용법: ")


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.asyncio
async def test_command_empty_expr(bot):
    event = bot.create_message("C1", "U1")
    expr = "  "
    help_text = "expected"
    await body(bot, event, expr, help_text)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == help_text


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.asyncio
async def test_command_bad_syntax(bot):
    event = bot.create_message("C1", "U1")
    expr = "1++"
    help_text = "help"
    await body(bot, event, expr, help_text)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"].startswith(
        "입력해주신 수식에 문법 오류가 있어요! ",
    )


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.asyncio
async def test_command_zero_division(bot):
    event = bot.create_message("C1", "U1")
    expr = "1/0"
    help_text = "help"
    await body(bot, event, expr, help_text)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert (
        said.data["text"]
        == "입력해주신 수식은 계산하다보면 0으로 나누기가 발생해서 계산할 수 없어요!"
    )


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.asyncio
async def test_command_timeout(bot):
    event = bot.create_message("C1", "U1")
    expr = "2**1000"
    help_text = "help"
    await body(bot, event, expr, help_text, timeout=0.0001)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert (
        said.data["text"]
        == "입력해주신 수식을 계산하려고 했지만 연산 시간이 너무 길어서 중단했어요!"
    )


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.asyncio
async def test_command_unexpected_error(bot):
    event = bot.create_message("C1", "U1")
    expr = "undefined_variable"
    help_text = "help"
    await body(bot, event, expr, help_text)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"].startswith(
        "예기치 않은 에러가 발생했어요! NameError",
    )


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.asyncio
async def test_command_short_expr(bot):
    event = bot.create_message("C1", "U1")
    expr = "1+2"
    help_text = "help"
    await body(bot, event, expr, help_text)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == "`1+2` == `3`"


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.asyncio
async def test_command_short_expr_empty_result(bot):
    event = bot.create_message("C1", "U1")
    expr = "''"
    help_text = "help"
    await body(bot, event, expr, help_text)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == "`''` == _Empty_"


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.asyncio
async def test_command_multiline_expr(bot):
    event = bot.create_message("C1", "U1")
    expr = "1+\\\n2"
    help_text = "help"
    await body(bot, event, expr, help_text)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert (
        said.data["text"] == "*Input*\n```\n1+\\\n2\n```\n*Output*\n```\n3\n```"
    )


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.asyncio
async def test_command_multiline_expr_empty_result(bot):
    event = bot.create_message("C1", "U1")
    expr = "'''\n'''[1:]"
    help_text = "help"
    await body(bot, event, expr, help_text, decimal_mode=False)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == f"*Input*\n```\n{expr}\n```\n*Output*\n_Empty_"


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.asyncio
async def test_command_locals(bot):
    event = bot.create_message("C1", "U1")
    expr = "sao = '키리토'"
    help_text = "help"
    await body(bot, event, expr, help_text, decimal_mode=False)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert (
        said.data["text"]
        == f"*Input*\n```\n{expr}\n```\n*Local State*\n```\nsao = '키리토'\n```"
    )


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.asyncio
async def test_command_none(bot):
    event = bot.create_message("C1", "U1")
    expr = "None"
    help_text = "help"
    await body(bot, event, expr, help_text, decimal_mode=False)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert (
        said.data["text"]
        == "입력해주신 수식을 계산했지만 아무런 값도 나오지 않았어요!"
    )


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


def test_scope_stack():
    scope = ScopeStack()

    with pytest.raises(NameError):
        _ = scope["undefined"]

    with pytest.raises(NameError):
        del scope["undefined"]


def test_annassign():
    e = Evaluator()

    err = "You can not use annotation syntax"
    with pytest.raises(BadSyntax, match=err):
        e.run("a: int = 10")

    assert "a" not in e.scope


def test_assert():
    e = Evaluator()
    err = "You can not use assertion syntax"
    with pytest.raises(BadSyntax, match=err):
        e.run("assert True")

    with pytest.raises(BadSyntax, match=err):
        e.run("assert False")


def test_assign():
    e = Evaluator()
    e.run("a = 1 + 2")
    assert e.scope["a"] == 3
    e.run("x, y = 10, 20")
    assert e.scope["x"] == 10
    assert e.scope["y"] == 20

    e.scope["dt"] = datetime.now()
    err = "This assign method is not allowed"
    with pytest.raises(BadSyntax, match=err):
        e.run("dt.year = 2000")

    err = "too many values to unpack"
    with pytest.raises(ValueError, match=err):
        e.run("year, month, day = 1,")

    err = "not enough values to unpack"
    with pytest.raises(ValueError, match=err):
        e.run('id, name = 1, "kirito", "black"')

    err = "cannot unpack non-iterable int object"
    with pytest.raises(TypeError, match=err):
        e.run("year, month, day = 1")

    e.run("arr = [1, 2, 3]")
    assert e.scope["arr"] == [1, 2, 3]

    e.run("arr[1] = 5")
    assert e.scope["arr"] == [1, 5, 3]

    e.run("arr[:] = [10, 20, 30]")
    assert e.scope["arr"] == [10, 20, 30]


def test_asyncfor():
    e = Evaluator()
    e.scope["r"] = 0
    err = "You can not use `async for` loop syntax"
    with pytest.raises(BadSyntax, match=err):
        e.run(
            """
async for x in [1, 2, 3, 4]:
    r += x

""",
        )
    assert e.scope["r"] == 0


def test_asyncfunctiondef():
    e = Evaluator()
    err = "Defining new coroutine via def syntax is not allowed"
    with pytest.raises(BadSyntax, match=err):
        e.run(
            """
async def abc():
    pass

""",
        )
    assert "abc" not in e.scope


def test_asyncwith():
    e = Evaluator()
    e.scope["r"] = 0
    err = "You can not use `async with` syntax"
    with pytest.raises(BadSyntax, match=err):
        e.run(
            """
async with x():
    r += 100

""",
        )
    assert e.scope["r"] == 0


def test_attribute():
    e = Evaluator()
    e.scope["dt"] = datetime.now()
    e.run("x = dt.year")
    assert e.scope["x"] == e.scope["dt"].year

    err = "You can not access `test_test_test` attribute"
    with pytest.raises(BadSyntax, match=err):
        e.run("y = dt.test_test_test")

    assert "y" not in e.scope

    err = "You can not access `asdf` attribute"
    with pytest.raises(BadSyntax, match=err):
        e.run("z = x.asdf")

    e.scope["math"] = math
    err = "You can not access `__module__` attribute"
    with pytest.raises(BadSyntax, match=err):
        e.run("math.__module__")

    e.scope["datetime"] = datetime
    err = "You can not access `test_test` attribute"
    with pytest.raises(BadSyntax, match=err):
        e.run("datetime.test_test")

    err = "You can not access attributes of "
    with pytest.raises(BadSyntax, match=err):
        e.run("Decimal.test_test")


def test_augassign():
    e = Evaluator()
    e.scope["a"] = 0
    e.run("a += 1")
    assert e.scope["a"] == 1
    e.scope["l"] = [1, 2, 3, 4]
    e.run("l[0] -= 1")
    assert e.scope["l"] == [0, 2, 3, 4]

    err = "This assign method is not allowed"
    with pytest.raises(BadSyntax, match=err):
        e.run("l[2:3] += 20")

    e.scope["dt"] = datetime.now()
    err = "This assign method is not allowed"
    with pytest.raises(BadSyntax, match=err):
        e.run("dt.year += 2000")


def test_await():
    e = Evaluator()
    err = "You can not await anything"
    with pytest.raises(BadSyntax, match=err):
        e.run("r = await x()")
    assert "r" not in e.scope


def test_binop():
    e = Evaluator()
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


def test_boolop():
    e = Evaluator()
    assert e.run("True and False") is (True and False)  # noqa: SIM223
    assert e.run("True or False") is (True or False)  # noqa: SIM222


def test_break():
    e = Evaluator()
    e.run("break")
    assert e.current_interrupt.__class__.__name__ == "Break"


def test_bytes():
    e = Evaluator()
    assert e.run('b"asdf"') == b"asdf"
    e.run('a = b"asdf"')
    assert e.scope["a"] == b"asdf"


def test_call():
    e = Evaluator()
    e.scope["date"] = date
    e.run("x = date(2019, 10, day=7)")
    assert e.scope["x"] == date(2019, 10, day=7)

    e.scope["math"] = math
    e.run("y = math.sqrt(121)")
    assert e.scope["y"] == math.sqrt(121)

    e.scope["datetime"] = datetime
    e.run("z = datetime.now().date()")
    assert e.scope["z"] == datetime.now().date()


def test_classdef():
    e = Evaluator()
    err = "Defining new class via def syntax is not allowed"
    with pytest.raises(BadSyntax, match=err):
        e.run(
            """
class ABCD:
    pass

""",
        )
    assert "ABCD" not in e.scope


def test_compare():
    e = Evaluator()
    assert e.run("1 == 2") is (1 == 2)  # noqa: PLR0133
    assert e.run("3 > 2") is (3 > 2)  # noqa: PLR0133
    assert e.run("3 >= 2") is (3 >= 2)  # noqa: PLR0133
    assert e.run('"A" in "America"') is ("A" in "America")  # noqa: PLR0133
    assert e.run('"E" not in "America"') is (
        "E" not in "America"  # noqa: PLR0133
    )
    assert e.run("1 is 2") is (1 is 2)  # noqa: F632 PLR0133
    assert e.run("1 is not 2") is (1 is not 2)  # noqa: F632 PLR0133
    assert e.run("3 < 2") is (3 < 2)  # noqa: PLR0133
    assert e.run("3 <= 2") is (3 <= 2)  # noqa: PLR0133


def test_constant():
    e1 = Evaluator()
    e2 = Evaluator(decimal_mode=True)
    assert e1.run("1.2") == 1.2
    assert e2.run("1.2") == D("1.2")


def test_continue():
    e = Evaluator()
    e.run("continue")
    assert e.current_interrupt.__class__.__name__ == "Continue"


def test_delete():
    e = Evaluator()
    e.scope["a"] = 0
    e.scope["b"] = 0
    e.scope["c"] = 0
    e.scope["d"] = 0
    e.run("del a, b, c")
    assert "a" not in e.scope
    assert "b" not in e.scope
    assert "c" not in e.scope
    assert "d" in e.scope
    e.run("del d")
    assert "d" not in e.scope
    e.scope["l"] = [1, 2, 3, 4]
    e.run("del l[0]")
    assert e.scope["l"] == [2, 3, 4]

    err = "This delete method is not allowed"
    with pytest.raises(BadSyntax, match=err):
        e.run("del l[2:3]")

    e.scope["dt"] = datetime.now()
    err = "This delete method is not allowed"
    with pytest.raises(BadSyntax, match=err):
        e.run("del dt.year")


def test_dict():
    e = Evaluator()
    assert e.run("{1: 111, 2: 222}") == {1: 111, 2: 222}
    e.run("a = {1: 111, 2: 222}")
    assert e.scope["a"] == {1: 111, 2: 222}


def test_dictcomp():
    e = Evaluator()
    assert e.run("{k+1: v**2 for k, v in {1: 1, 2: 11, 3: 111}.items()}") == {
        2: 1,
        3: 121,
        4: 12321,
    }
    assert "k" not in e.scope
    assert "v" not in e.scope

    e.run("a = {k+1: v**2 for k, v in {1: 1, 2: 11, 3: 111}.items()}")
    assert e.scope["a"] == {
        2: 1,
        3: 121,
        4: 12321,
    }
    assert "k" not in e.scope
    assert "v" not in e.scope

    e.run("k = 'test k'")
    e.run("v = 'test v'")
    assert e.run("{k+1: v**2 for k, v in {1: 1, 2: 11, 3: 111}.items()}") == {
        2: 1,
        3: 121,
        4: 12321,
    }
    assert e.scope["k"] == "test k"
    assert e.scope["v"] == "test v"

    assert e.run(
        "{k: v for k in [1, 2, 3] for v in [11, 22, 33] if k % 2 == 0 if v % 2 == 1}",
    ) == {2: 33}
    assert e.scope["k"] == "test k"
    assert e.scope["v"] == "test v"


def test_ellipsis():
    e = Evaluator()
    assert e.run("...") == Ellipsis


def test_expr():
    e = Evaluator()
    assert e.run("True") is True
    assert e.run("False") is False
    assert e.run("None") is None
    assert e.run("123") == 123
    assert e.run('"abc"') == "abc"
    assert e.run("[1, 2, 3]") == [1, 2, 3]
    assert e.run("(1, 2, 3, 3)") == (1, 2, 3, 3)
    assert e.run("{1, 2, 3, 3}") == {1, 2, 3}
    assert e.run("{1: 111, 2: 222}") == {1: 111, 2: 222}
    with pytest.raises(NameError):
        e.run("undefined_variable")


def test_functiondef():
    e = Evaluator()
    err = "Defining new function via def syntax is not allowed"
    with pytest.raises(BadSyntax, match=err):
        e.run(
            """
def abc():
    pass

""",
        )
    assert "abc" not in e.scope


def test_for():
    total = 0
    for x in [1, 2, 3, 4, 5, 6]:
        total = total + x
        if total > 10:
            continue
        total = total * 2
    else:  # noqa: PLW0120
        total = total + 10000
    e = Evaluator()
    e.run(
        """
total = 0
for x in [1, 2, 3, 4, 5, 6]:
    total = total + x
    if total > 10:
        continue
    total = total * 2
else:
    total = total + 10000
""",
    )
    assert e.scope["total"] == total

    total2 = 0
    for x in [1, 2, 3, 4, 5, 6]:
        total2 = total2 + x
        if total2 > 10:
            break
        total2 = total2 * 2
    else:
        total2 = total2 + 10000

    e.run(
        """
total2 = 0
for x in [1, 2, 3, 4, 5, 6]:
    total2 = total2 + x
    if total2 > 10:
        break
    total2 = total2 * 2
else:
    total2 = total2 + 10000
""",
    )
    assert e.scope["total2"] == total2


def test_formattedvalue():
    e = Evaluator()
    e.scope["before"] = 123456
    e.run('after = f"change {before} to {before:,}!"')
    assert e.scope["after"] == "change 123456 to 123,456!"


def test_generator_exp():
    e = Evaluator()
    e.scope["r"] = [1, 2, 3]
    err = "Defining new generator expression is not allowed"
    with pytest.raises(BadSyntax, match=err):
        e.run("x = (i ** 2 for i in r)")
    assert "x" not in e.scope


def test_global():
    e = Evaluator()
    err = "You can not use `global` syntax"
    with pytest.raises(BadSyntax, match=err):
        e.run("global x")


def test_if():
    e = Evaluator()
    e.scope["a"] = 1
    e.run(
        """
if a == 1:
    a = 2
    b = 3
""",
    )
    assert e.scope["a"] == 2
    assert e.scope["b"] == 3

    e.run(
        """
if a == 1:
    a = 2
    b = 3
    z = 1
else:
    a = 3
    b = 4
    c = 5
""",
    )
    assert e.scope["a"] == 3
    assert e.scope["b"] == 4
    assert e.scope["c"] == 5
    assert "z" not in e.scope

    e.run(
        """
if a == 1:
    a = 2
    b = 3
    z = 1
elif a == 3:
    d = 4
    e = 5
    f = 6
else:
    a = 3
    b = 4
    c = 5
    y = 7
""",
    )
    assert e.scope["a"] == 3
    assert e.scope["b"] == 4
    assert e.scope["c"] == 5
    assert e.scope["d"] == 4
    assert e.scope["e"] == 5
    assert e.scope["f"] == 6
    assert "y" not in e.scope
    assert "z" not in e.scope


def test_ifexp():
    e = Evaluator()
    assert e.run("100 if 1 == 1 else 200") == 100
    assert e.run("100 if 1 == 2 else 200") == 200


def test_import():
    e = Evaluator()
    err = "You can not import anything"
    with pytest.raises(BadSyntax, match=err):
        e.run("import sys")
    assert "sys" not in e.scope


def test_importfrom():
    e = Evaluator()
    err = "You can not import anything"
    with pytest.raises(BadSyntax, match=err):
        e.run("from os import path")
    assert "path" not in e.scope


def test_lambda():
    e = Evaluator()
    err = "Defining new function via lambda syntax is not allowed"
    with pytest.raises(BadSyntax, match=err):
        e.run("lambda x: x*2")


def test_list():
    e = Evaluator()
    assert e.run("[1, 2, 3]") == [1, 2, 3]
    e.run("a = [1, 2, 3]")
    assert e.scope["a"] == [1, 2, 3]


def test_listcomp():
    e = Evaluator()
    assert e.run("[x ** 2 for x in [1, 2, 3]]") == [1, 4, 9]
    assert "x" not in e.scope

    assert e.run("[x ** 2 + y for x in [1, 2, 3] for y in [10, 20, 30]]") == (
        [x**2 + y for x in [1, 2, 3] for y in [10, 20, 30]]
    )
    assert "x" not in e.scope
    assert "y" not in e.scope

    assert e.run("[y ** 2 for x in [1, 2, 3] for y in [x+1, x+3, x+5]]") == (
        [y**2 for x in [1, 2, 3] for y in [x + 1, x + 3, x + 5]]
    )
    assert "x" not in e.scope
    assert "y" not in e.scope

    e.run("x = 'test x'")
    e.run("y = 'test y'")
    assert e.run("[y ** 2 for x in [1, 2, 3] for y in [x+1, x+3, x+5]]") == (
        [y**2 for x in [1, 2, 3] for y in [x + 1, x + 3, x + 5]]
    )
    assert e.scope["x"] == "test x"
    assert e.scope["y"] == "test y"

    assert e.run(
        "[x + y for x in [1, 2, 3] for y in [11, 22, 33] if x % 2 == 0 if y % 2 == 1]",
    ) == [13, 35]
    assert e.scope["x"] == "test x"
    assert e.scope["y"] == "test y"


def test_name():
    e = Evaluator()
    assert e.run("int") is int


def test_nameconstant():
    e = Evaluator()
    assert e.run("True") is True
    assert e.run("False") is False
    assert e.run("None") is None
    e.run("x = True")
    e.run("y = False")
    e.run("z = None")
    assert e.scope["x"] is True
    assert e.scope["y"] is False
    assert e.scope["z"] is None


def test_nonlocal():
    e = Evaluator()
    err = "You can not use `nonlocal` syntax"
    with pytest.raises(BadSyntax, match=err):
        e.run("nonlocal x")


def test_num():
    e = Evaluator()
    assert e.run("123") == 123
    e.run("a = 123")
    assert e.scope["a"] == 123


def test_pass():
    e = Evaluator()
    e.run("pass")


def test_raise():
    e = Evaluator()
    err = "You can not use `raise` syntax"
    with pytest.raises(BadSyntax, match=err):
        e.run("raise NameError")


def test_return():
    e = Evaluator()
    err = "You can not use `return` syntax"
    with pytest.raises(BadSyntax, match=err):
        e.run("return True")


def test_set():
    e = Evaluator()
    assert e.run("{1, 1, 2, 3, 3}") == {1, 2, 3}
    e.run("a = {1, 1, 2, 3, 3}")
    assert e.scope["a"] == {1, 2, 3}


def test_setcomp():
    e = Evaluator()
    assert e.run("{x ** 2 for x in [1, 2, 3, 3]}") == {1, 4, 9}
    assert "x" not in e.scope

    assert e.run("{x ** 2 + y for x in [1, 2, 3] for y in [10, 20, 30]}") == (
        {x**2 + y for x in [1, 2, 3] for y in [10, 20, 30]}
    )
    assert "x" not in e.scope
    assert "y" not in e.scope

    assert e.run("{y ** 2 for x in [1, 2, 3] for y in [x+1, x+3, x+5]}") == (
        {y**2 for x in [1, 2, 3] for y in [x + 1, x + 3, x + 5]}
    )
    assert "x" not in e.scope
    assert "y" not in e.scope

    e.run("x = 'test x'")
    e.run("y = 'test y'")
    assert e.run("{y ** 2 for x in [1, 2, 3] for y in [x+1, x+3, x+5]}") == (
        {y**2 for x in [1, 2, 3] for y in [x + 1, x + 3, x + 5]}
    )
    assert e.scope["x"] == "test x"
    assert e.scope["y"] == "test y"

    assert e.run(
        "{x + y for x in [1, 2, 3] for y in [11, 22, 33] if x % 2 == 0 if y % 2 == 1}",
    ) == {13, 35}
    assert e.scope["x"] == "test x"
    assert e.scope["y"] == "test y"


def test_slice():
    e = Evaluator()
    e.scope["obj"] = GetItemSpy()
    e.run("obj[10:20:3]")
    s = e.scope["obj"].queue.pop()
    assert isinstance(s, slice)
    assert s.start == 10
    assert s.stop == 20
    assert s.step == 3


def test_str():
    e = Evaluator()
    assert e.run('"asdf"') == "asdf"
    e.run('a = "asdf"')
    assert e.scope["a"] == "asdf"


def test_subscript():
    e = Evaluator()
    assert e.run("[10, 20, 30][0]") == 10
    assert e.run("(100, 200, 300)[0]") == 100
    assert e.run('{"a": 1000, "b": 2000, "c": 3000}["a"]') == 1000
    e.run("a = [10, 20, 30][0]")
    e.run("b = (100, 200, 300)[0]")
    e.run('c = {"a": 1000, "b": 2000, "c": 3000}["a"]')
    assert e.scope["a"] == 10
    assert e.scope["b"] == 100
    assert e.scope["c"] == 1000
    e.scope["l"] = [11, 22, 33]
    assert e.run("l[2]") == 33
    e.run("l[2] = 44")
    assert e.scope["l"] == [11, 22, 44]


def test_try():
    e = Evaluator()
    err = "You can not use `try` syntax"
    with pytest.raises(BadSyntax, match=err):
        e.run(
            """
try:
    x = 1
except:
    pass
""",
        )
    assert "x" not in e.scope


def test_trystar():
    e = Evaluator()
    err = "You can not use `try` syntax with star"
    with pytest.raises(BadSyntax, match=err):
        e.run(
            """
try:
    x = 1
except* Exception:
    pass
""",
        )
    assert "x" not in e.scope


def test_tuple():
    e = Evaluator()
    assert e.run("(1, 1, 2, 3, 3)") == (1, 1, 2, 3, 3)
    e.run("a = (1, 1, 2, 3, 3)")
    assert e.scope["a"] == (1, 1, 2, 3, 3)


def test_typealias():
    e = Evaluator()
    err = "You can not define type alias"
    with pytest.raises(BadSyntax, match=err):
        e.run(
            """
type Number = int
""",
        )
    assert "Number" not in e.scope


def test_unaryop():
    e = Evaluator()
    assert e.run("~100") == ~100
    assert e.run("not 100") == (not 100)
    assert e.run("+100") == +100
    assert e.run("-100") == -100


def test_while():
    total = 0
    i = 1
    while total > 100:
        total += i
        i += i
        if i % 10 == 0:
            i += 1
    else:  # noqa: PLW0120
        total = total + 10000
    e = Evaluator()
    e.run(
        """
total = 0
i = 1
while total > 100:
    total += i
    i += i
    if i % 10 == 0:
        i += 1
else:
    total = total + 10000
""",
    )
    assert e.scope["total"] == total

    r = 0
    while True:
        break
    else:
        r += 10

    e.run(
        """
r = 0
while True:
    break
else:
    r += 10
""",
    )
    assert e.scope["r"] == 0


def test_with():
    e = Evaluator()
    err = "You can not use `with` syntax"
    with pytest.raises(BadSyntax, match=err):
        e.run(
            """
with some:
    x = 1
""",
        )
    assert "x" not in e.scope


def test_yield():
    e = Evaluator()
    err = "You can not use `yield` syntax"
    with pytest.raises(BadSyntax, match=err):
        e.run("x = yield f()")
    assert "x" not in e.scope


def test_yield_from():
    e = Evaluator()
    err = "You can not use `yield from` syntax"
    with pytest.raises(BadSyntax, match=err):
        e.run("x = yield from f()")
    assert "x" not in e.scope


@pytest_asyncio.fixture()
async def bot():
    return FakeBot(
        loop=asyncio.get_running_loop(),
        process_pool_executor=ProcessPoolExecutor(),
    )


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.asyncio
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
