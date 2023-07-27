import datetime
import shlex

import pytest

from yui.box import Box
from yui.box.apps.basic import App
from yui.box.parsers import parse_option_and_arguments
from yui.command.decorators import argument
from yui.command.decorators import option
from yui.transform import str_to_date
from yui.transform import value_range


def test_parse_option_and_arguments():
    box = Box()

    def callable_default():
        return "hello"

    @box.command("test-option")
    @option("--required-option", required=True)
    @option("--dest-change-option", dest="dest_changed_option")
    @option("--is-flag", is_flag=True)
    @option("--multiple", multiple=True)
    @option("--container", container_cls=set, type_=float, nargs=2)
    @option("--callable-default", default=callable_default)
    @option("--non-type")
    @option("--default-option", default="!!!")
    @option("--transform", type_=int, transform_func=value_range(1, 10))
    @option("--transform-non-type", transform_func=str_to_date())
    @option(
        "--transform-container",
        type_=int,
        transform_func=value_range(1, 10),
        container_cls=set,
        nargs=3,
    )
    @option(
        "--transform-two",
        transform_func=str_to_date(),
        container_cls=list,
        nargs=2,
    )
    async def test_option(
        required_option: int,
        dest_changed_option: int,
        is_flag: bool,
        multiple: list[int],
        container,
        callable_default: str,
        non_type,
        default_option,
        transform: int,
        transform_non_type: datetime.date,
        transform_container: set[int],
        transform_two: list[datetime.date],
    ):
        pass

    app: App = box.apps.pop()

    chunks = shlex.split(
        "--dest-change-option=2222 "
        "--is-flag "
        "--multiple 3333 --multiple=4444 "
        "--container 55.55 66.66 "
        "--non-type world "
        "--transform 4 "
        "--transform-non-type 2017-10-07 "
        "--transform-container 4 6 2 "
        "--transform-two 2017-10-07 2017-10-24 "
        "--required-option 1111 ",
    )

    kw, remain_chunks = parse_option_and_arguments(app.handler, chunks)
    assert kw["required_option"] == 1111
    assert kw["dest_changed_option"] == 2222
    assert kw["is_flag"]
    assert kw["multiple"] == [3333, 4444]
    assert kw["container"] == {55.55, 66.66}
    assert kw["callable_default"] == "hello"
    assert kw["non_type"] == "world"
    assert kw["default_option"] == "!!!"
    assert kw["transform"] == 4
    assert kw["transform_non_type"] == datetime.date(2017, 10, 7)
    assert kw["transform_container"] == {2, 4, 6}
    assert kw["transform_two"] == [
        datetime.date(2017, 10, 7),
        datetime.date(2017, 10, 24),
    ]
    assert not remain_chunks

    chunks = shlex.split("")

    with pytest.raises(SyntaxError) as e:
        parse_option_and_arguments(app.handler, chunks)
    assert (
        e.value.msg
        == "--required-option: incorrect option value count."
        " expected 1, 0 given."
    )

    chunks = shlex.split("--required-option 1111 --container 55.55 ")

    with pytest.raises(SyntaxError) as e:
        parse_option_and_arguments(app.handler, chunks)
    assert (
        e.value.msg
        == "--container: incorrect option value count. expected 2, 1 given."
    )

    chunks = shlex.split("--required-option 1111 --container a b ")

    with pytest.raises(SyntaxError) as e:
        parse_option_and_arguments(app.handler, chunks)
    assert (
        e.value.msg
        == "--container: invalid type of option value"
        "(Can not find matching caster)"
    )

    chunks = shlex.split(
        "--required-option 1111 --transform-non-type 2017-10-99",
    )

    with pytest.raises(SyntaxError) as e:
        parse_option_and_arguments(app.handler, chunks)
    assert (
        e.value.msg
        == "--transform-non-type: fail to transform option "
        "value (day is out of range for month)"
    )

    chunks = shlex.split(
        "--required-option 1111 --transform-two 2017-10-99 2017-10-00",
    )

    with pytest.raises(SyntaxError) as e:
        parse_option_and_arguments(app.handler, chunks)
    assert (
        e.value.msg
        == "--transform-two: fail to transform option "
        "value (day is out of range for month)"
    )

    @box.command("test-argument1")
    @argument("non_type")
    @argument("transform_non_type", transform_func=str_to_date())
    @argument("container", nargs=3, container_cls=set, type_=float)
    @argument("container_with_typing", nargs=3)
    @argument(
        "container_with_transform",
        nargs=2,
        container_cls=list,
        transform_func=str_to_date(),
    )
    async def test_argument1(
        non_type,
        transform_non_type: datetime.date,
        container_with_typing: list[int],
        container_with_transform: list[datetime.date],
    ):
        pass

    app: App = box.apps.pop()

    chunks = shlex.split(
        "hello 2017-10-07 3.3 1.1 2.2 1 2 3 2017-10-07 2017-10-24 ",
    )

    kw, remain_chunks = parse_option_and_arguments(app.handler, chunks)

    assert kw["non_type"] == "hello"
    assert kw["transform_non_type"] == datetime.date(2017, 10, 7)
    assert kw["container"] == {1.1, 2.2, 3.3}
    assert kw["container_with_typing"] == [1, 2, 3]
    assert kw["container_with_transform"] == [
        datetime.date(2017, 10, 7),
        datetime.date(2017, 10, 24),
    ]

    @box.command("test-argument2")
    @argument("args", nargs=-1)
    async def test_argument2(args):
        pass

    app: App = box.apps.pop()

    chunks = shlex.split("")

    with pytest.raises(SyntaxError) as e:
        parse_option_and_arguments(app.handler, chunks)
    assert (
        e.value.msg
        == "args: incorrect argument value count. expected >0, 0 given."
    )

    @box.command("test-argument3")
    @argument("args", nargs=2)
    @argument("concat", nargs=3, concat=True)
    async def test_argument3(args):
        pass

    app: App = box.apps.pop()

    chunks = shlex.split("1")

    with pytest.raises(SyntaxError) as e:
        parse_option_and_arguments(app.handler, chunks)
    assert (
        e.value.msg
        == "args: incorrect argument value count. expected 2, 1 given."
    )

    chunks = shlex.split("1 2 hell o world")

    kw, remain_chunks = parse_option_and_arguments(app.handler, chunks)
    assert kw["args"] == ("1", "2")
    assert kw["concat"] == "hell o world"
    assert not remain_chunks

    @box.command("test-argument4")
    @argument("args")
    async def test_argument4(args: int):
        pass

    app: App = box.apps.pop()

    chunks = shlex.split("asdf")

    with pytest.raises(SyntaxError) as e:
        parse_option_and_arguments(app.handler, chunks)
    assert (
        e.value.msg
        == "args: invalid type of argument value(Can not find matching caster)"
    )

    @box.command("test-argument5")
    @argument("args", transform_func=str_to_date())
    async def test_argument5(args):
        pass

    app: App = box.apps.pop()

    chunks = shlex.split("2017-10-99")

    with pytest.raises(SyntaxError) as e:
        parse_option_and_arguments(app.handler, chunks)
    assert (
        e.value.msg
        == "args: fail to transform argument value "
        "(day is out of range for month)"
    )

    @box.command("test-argument6")
    @argument("args", nargs=2, transform_func=str_to_date())
    async def test_argument6(args):
        pass

    app: App = box.apps.pop()

    chunks = shlex.split("2017-10-99 2017-10-00")

    with pytest.raises(SyntaxError) as e:
        parse_option_and_arguments(app.handler, chunks)
    assert (
        e.value.msg
        == "args: fail to transform argument value "
        "(day is out of range for month)"
    )
